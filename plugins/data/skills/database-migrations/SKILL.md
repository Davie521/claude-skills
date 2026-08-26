---
name: database-migrations
description: Database migration best practices for schema changes, data migrations, rollbacks, and zero-downtime deployments in PostgreSQL with Prisma, Drizzle, Kysely, and Alembic — plus a PostgreSQL quick reference for query optimization, indexing, schema design, and Row Level Security. Use when writing SQL queries or migrations, designing Postgres schemas or indexes, troubleshooting slow queries, implementing RLS, or planning zero-downtime schema changes.
origin: ECC
---

# Database Migration Patterns

Safe, reversible database schema changes for production systems.

## When to Activate

- Creating or altering database tables
- Adding/removing columns or indexes
- Running data migrations (backfill, transform)
- Planning zero-downtime schema changes
- Setting up migration tooling for a new project
- Writing SQL queries or designing PostgreSQL schemas
- Troubleshooting slow queries
- Implementing Row Level Security

## Core Principles

1. **Every change is a migration** — never alter production databases manually
2. **Migrations are forward-only in production** — rollbacks use new forward migrations
3. **Schema and data migrations are separate** — never mix DDL and DML in one migration
4. **Test migrations against production-sized data** — a migration that works on 100 rows may lock on 10M
5. **Migrations are immutable once deployed** — never edit a migration that has run in production

## Migration Safety Checklist

Before applying any migration:

- [ ] Migration has both UP and DOWN (or is explicitly marked irreversible)
- [ ] Long-held full table locks avoided on large tables (use concurrent operations)
- [ ] Every `ALTER TABLE` runs under a `lock_timeout` with retry — an ACCESS EXCLUSIVE subform waiting in the queue blocks all traffic behind it
- [ ] New columns are nullable or have a *non-volatile* default (a volatile default rewrites the table)
- [ ] Indexes created concurrently (not inline with CREATE TABLE for existing tables)
- [ ] Data backfill is a separate migration from schema change
- [ ] Tested against a copy of production data
- [ ] Rollback plan documented

## PostgreSQL Patterns

### Adding a Column Safely

**`ADD COLUMN` takes an ACCESS EXCLUSIVE lock, even the "instant" ones.**
No rewrite ≠ no lock. The risk is not the ALTER's own duration — it is the lock
queue: the ALTER waits for existing transactions on the table to finish, and
every new query queues *behind the ALTER* while it waits. One long-running
`SELECT` turns a millisecond DDL into a full table stall.

Most `ALTER TABLE` subforms take ACCESS EXCLUSIVE, but not all — and the docs
note *most*, not every, exception. `VALIDATE CONSTRAINT` and `SET STATISTICS`
take only SHARE UPDATE EXCLUSIVE; `ADD FOREIGN KEY` and `ENABLE`/`DISABLE
TRIGGER` take SHARE ROW EXCLUSIVE. Two traps make "look up the subform"
insufficient on its own — both measured on PostgreSQL 18.6:

- **The level can depend on the parameter, not just the subform.**
  `SET (fillfactor=80)` takes SHARE UPDATE EXCLUSIVE, but
  `SET (user_catalog_table=true)` takes ACCESS EXCLUSIVE. Only the fillfactor,
  TOAST, autovacuum and `parallel_workers` parameters are documented as weaker;
  the rest fall back to the default.
- **One statement can lock several tables at different levels.**
  `ATTACH PARTITION` takes SHARE UPDATE EXCLUSIVE on the parent but ACCESS
  EXCLUSIVE on *both* the partition being attached and any existing DEFAULT
  partition — so attaching to a partitioned table that has a default partition
  blocks that default partition completely.

When it matters, measure with `pg_locks` on your own version rather than
reasoning from the docs' "unless explicitly noted" rule.

### The DDL Execution Envelope

Every `ALTER TABLE` in this file assumes this wrapper. It is not repeated in
each example — apply it every time:

```sql
BEGIN;
SET LOCAL lock_timeout = '3s';   -- SET LOCAL is a no-op outside a transaction:
ALTER TABLE users ADD COLUMN avatar_url TEXT;   -- it only warns, and the
COMMIT;                                         -- timeout silently stays 0
```

On `canceling statement due to lock timeout`, retry the whole transaction with
backoff. The timeout is what bounds how long the ALTER sits at the head of the
lock queue with all other traffic stacked behind it.

**Non-transactional DDL cannot use this envelope.** `CREATE INDEX CONCURRENTLY`
must run outside a transaction, so set `lock_timeout` at session level on a
dedicated connection, and `RESET` it or close that connection afterwards rather
than leaking the setting into pooled traffic.

```sql
-- GOOD: nullable column — catalog-only change, no rewrite (still ACCESS EXCLUSIVE)
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- GOOD: non-volatile default — Postgres 11+ stores it in the catalog, no rewrite
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- BAD: volatile default (gen_random_uuid/random/clock_timestamp) — DOES rewrite
-- the whole table, holding the lock throughout.
-- Note now() and current_timestamp are STABLE, not volatile: they do NOT
-- rewrite. But every existing row gets one identical value — the transaction's
-- START time, not the moment this statement ran. Under a runner that wraps the
-- whole migration run in one transaction, that can be minutes earlier.
ALTER TABLE users ADD COLUMN public_id UUID NOT NULL DEFAULT gen_random_uuid();

-- BAD: NOT NULL without a default on a non-empty table.
-- This does NOT rewrite — it fails outright:
--   ERROR: column "role" of relation "users" contains null values
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
```

### Making an Existing Column NOT NULL

**Precondition: application code must already write the column on every insert
and update.** A `NOT VALID` constraint skips the scan of existing rows but is
enforced on new writes immediately — including updates that don't touch the
column. Add it while a writer can still produce NULL and ordinary traffic starts
failing for the entire backfill window. Deploy the writing code first, then:

```sql
-- 1. Add the constraint as NOT VALID (cheap: no full-table scan, brief lock)
ALTER TABLE users ADD CONSTRAINT users_role_not_null
  CHECK (role IS NOT NULL) NOT VALID;

-- 2. Backfill the existing NULL rows (batched — see Large Data Migrations),
--    then validate. The scan takes only SHARE UPDATE EXCLUSIVE, so reads and
--    writes continue.
ALTER TABLE users VALIDATE CONSTRAINT users_role_not_null;

-- 3. Postgres 12+ skips the scan when a VALIDATED CHECK proves the column is
--    non-null. It must literally test `IS NOT NULL`. CHECK (role <> '') not
--    only fails to qualify, it does not enforce non-null at all: NULL <> ''
--    evaluates to UNKNOWN, and a CHECK constraint passes on UNKNOWN.
ALTER TABLE users ALTER COLUMN role SET NOT NULL;
ALTER TABLE users DROP CONSTRAINT users_role_not_null;
```

The CHECK above is a *bridge* for PostgreSQL 12–17. **PostgreSQL 18 supports an
invalid NOT NULL constraint directly**, which removes the bridge entirely:

```sql
-- PG 18+ only. Note the syntax: ADD CONSTRAINT ... NOT NULL <column> NOT VALID.
-- (There is no `ALTER COLUMN ... SET NOT NULL NOT VALID` form — that is a
-- syntax error.)
ALTER TABLE users ADD CONSTRAINT users_role_nn NOT NULL role NOT VALID;
-- ... backfill ...
ALTER TABLE users VALIDATE CONSTRAINT users_role_nn;
ALTER TABLE users ALTER COLUMN role SET NOT NULL;
```

Same precondition applies: the invalid NOT NULL constraint rejects new NULLs
immediately, so the writing code must be deployed first.

### Adding an Index Without Downtime

```sql
-- BAD: Blocks writes on large tables
CREATE INDEX idx_users_email ON users (email);

-- GOOD: Non-blocking, allows concurrent writes
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);

-- Note: CONCURRENTLY cannot run inside a transaction block
-- Most migration tools need special handling for this
```

**A failed `CREATE INDEX CONCURRENTLY` leaves an invalid index behind.** It is
not rolled back and not cleaned up for you: the leftover index costs write
overhead on every insert and update while serving no reads. Check before you
retry, or you accumulate one per attempt:

```sql
SELECT indisvalid FROM pg_index WHERE indexrelid = 'idx_users_email'::regclass;
-- false  ->  DROP INDEX CONCURRENTLY idx_users_email;   then retry
--            or  REINDEX INDEX CONCURRENTLY idx_users_email;
```

### Renaming a Column (Zero-Downtime)

Never rename directly in production. Use the expand-contract pattern:

```sql
-- Step 1: Add new column (migration 001)
ALTER TABLE users ADD COLUMN display_name TEXT;

-- Step 2: Backfill data (migration 002, data migration)
UPDATE users SET display_name = username WHERE display_name IS NULL;

-- Step 3: Update application code to read/write both columns
-- Deploy application changes

-- Step 4: Stop writing to old column, drop it (migration 003)
ALTER TABLE users DROP COLUMN username;
```

### Removing a Column Safely

```sql
-- Step 1: Remove all application references to the column
-- Step 2: Deploy application without the column reference
-- Step 3: Drop column in next migration
ALTER TABLE orders DROP COLUMN legacy_status;
```

### Large Data Migrations

```sql
-- BAD: Updates all rows in one transaction. It does NOT block reads — an
-- UPDATE takes only ROW EXCLUSIVE on the table — but it holds a row lock on
-- every affected row until commit, bloats WAL, and keeps one snapshot open for
-- the whole run, which stalls vacuum.
UPDATE users SET normalized_email = LOWER(email);
```

**`COMMIT` inside `DO $$ ... $$` is only legal when the `DO` runs at the top
level.** If anything has already opened a transaction, it fails with
`ERROR: invalid transaction termination`. Whether that bites you depends on the
runner, and they differ — check yours rather than assuming:

| Runner | In a transaction? | Opt-out |
|---|---|---|
| Alembic | Yes — by default one transaction for the *whole run*, not per migration (`transaction_per_migration=False`) | `with op.get_context().autocommit_block():` |
| Rails | Yes, per migration | `disable_ddl_transaction!` |
| Flyway | Yes, per migration | A sidecar config file next to the migration — `V2__x.sql.conf` containing `executeInTransaction=false`. There is no in-SQL `-- flyway:` directive for this; a comment claiming to set it is silently ignored |
| Prisma (PostgreSQL) | No — Migrate does not wrap by default | n/a. Statement splitting changed across 7.x, and it still falls back to sending the whole file at once (which Postgres then wraps implicitly) when its parser hits syntax it does not handle. **Regardless of version, give `CREATE INDEX CONCURRENTLY` a migration file of its own** — that rule holds on every version and needs no version check |

Even where an opt-out exists, driving the loop from outside is usually better:
you get progress reporting, resumability after a failure, and pacing between
batches — none of which a single in-migration `DO` block gives you.

First give the batch predicate an index, or each batch re-scans a growing prefix
and the backfill degrades to O(n²) on exactly the large tables this is for:

```sql
CREATE INDEX CONCURRENTLY idx_users_backfill_pending
  ON users (id) WHERE normalized_email IS NULL;
-- Drop it when the backfill is done.
```

```bash
#!/usr/bin/env bash
set -uo pipefail
OUT=$(mktemp)                      # not a fixed path: concurrent backfills would clobber it
trap 'rm -f "$OUT"' EXIT
# Each psql invocation is its own transaction.
while :; do
  # Capture to a file: piping straight into wc discards psql's exit status,
  # which is how a failed batch gets mistaken for a finished one.
  psql "$DATABASE_URL" -qtAX -v ON_ERROR_STOP=1 -c "
    SET lock_timeout = '3s';
    WITH batch AS (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      ORDER BY id
      LIMIT 10000
      FOR UPDATE SKIP LOCKED
    )
    UPDATE users u SET normalized_email = LOWER(u.email)
    FROM batch WHERE u.id = batch.id
    RETURNING 1;" > "$OUT"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    # Lock timeout, deadlock, connection drop — NOT completion. Made likely by
    # the lock_timeout above, which is the point: fail loudly, then retry.
    echo "batch failed (exit $rc) — backfill is INCOMPLETE" >&2
    exit "$rc"
  fi
  n=$(wc -l < "$OUT" | tr -d ' ')
  echo "updated $n"
  [ "$n" -eq 0 ] && break
  sleep 0.5   # let replicas and autovacuum catch up
done

# SKIP LOCKED can return an empty batch while rows remain. Verify, don't assume.
# Same discipline as above: check psql's status before trusting its output.
psql "$DATABASE_URL" -qtAX -v ON_ERROR_STOP=1 \
  -c "SELECT count(*) FROM users WHERE normalized_email IS NULL;" > "$OUT" || {
    echo "verification query failed — backfill state unknown" >&2; exit 1; }
remaining=$(tr -d ' ' < "$OUT")
[ "$remaining" -eq 0 ] || { echo "still $remaining rows pending" >&2; exit 1; }
```

Three things this has to get right, and the naive version doesn't:

- **An error is not a completion.** `psql | wc -l` throws away psql's exit
  status: a lock timeout writes to stderr, leaves stdout empty, and `wc -l`
  dutifully reports 0 — so the loop breaks and declares success mid-backfill.
  Capture the output, check `$?`, and abort loudly.
- **`SKIP LOCKED` can make a batch return 0 while rows remain** (every remaining
  candidate happens to be locked). Treating 0 as "done" exits early. That is why
  the loop ends with a `count(*)` verification instead of trusting the counter.
- **Pause between batches.** Back-to-back batches on a large table outrun
  replication and autovacuum. The `sleep` is what keeps replica lag bounded.

If you must keep it in SQL, use a procedure and `CALL` it from a top-level
session — that permits `COMMIT`. Inside a runner that has already opened a
transaction it still does not, regardless of `CALL` vs `DO`.

## Prisma (TypeScript/Node.js)

### Workflow

```bash
# Create migration from schema changes
npx prisma migrate dev --name add_user_avatar

# Apply pending migrations in production
npx prisma migrate deploy

# Reset database (dev only)
npx prisma migrate reset

# Generate client after schema changes
npx prisma generate
```

### Schema Example

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  avatarUrl String?  @map("avatar_url")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  orders    Order[]

  @@map("users")
  @@index([email])
}
```

### Custom SQL Migration

For operations Prisma cannot express (concurrent indexes, data backfills):

```bash
# Create empty migration, then edit the SQL manually
npx prisma migrate dev --create-only --name add_email_index
```

```sql
-- migrations/20240115_add_email_index/migration.sql
-- Prisma cannot generate CONCURRENTLY, so we write it manually
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
```

## Drizzle (TypeScript/Node.js)

### Workflow

```bash
# Generate migration from schema changes
npx drizzle-kit generate

# Apply migrations
npx drizzle-kit migrate

# Push schema directly (dev only, no migration file)
npx drizzle-kit push
```

### Schema Example

```typescript
import { pgTable, text, timestamp, uuid, boolean } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});
```

## Kysely (TypeScript/Node.js)

### Workflow (kysely-ctl)

```bash
# Initialize config file (kysely.config.ts)
kysely init

# Create a new migration file
kysely migrate make add_user_avatar

# Apply all pending migrations
kysely migrate latest

# Rollback last migration
kysely migrate down

# Show migration status
kysely migrate list
```

### Migration File

```typescript
// migrations/2024_01_15_001_create_user_profile.ts
import { type Kysely, sql } from 'kysely'

// IMPORTANT: Always use Kysely<any>, not your typed DB interface.
// Migrations are frozen in time and must not depend on current schema types.
export async function up(db: Kysely<any>): Promise<void> {
  await db.schema
    .createTable('user_profile')
    .addColumn('id', 'serial', (col) => col.primaryKey())
    .addColumn('email', 'varchar(255)', (col) => col.notNull().unique())
    .addColumn('avatar_url', 'text')
    .addColumn('created_at', 'timestamp', (col) =>
      col.defaultTo(sql`now()`).notNull()
    )
    .execute()

  await db.schema
    .createIndex('idx_user_profile_avatar')
    .on('user_profile')
    .column('avatar_url')
    .execute()
}

export async function down(db: Kysely<any>): Promise<void> {
  await db.schema.dropTable('user_profile').execute()
}
```

### Programmatic Migrator

```typescript
import { Migrator, FileMigrationProvider } from 'kysely'
import { promises as fs } from 'fs'
import * as path from 'path'
// ESM only — CJS can use __dirname directly
import { fileURLToPath } from 'url'
const migrationFolder = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  './migrations',
)

// `db` is your Kysely<any> database instance
const migrator = new Migrator({
  db,
  provider: new FileMigrationProvider({
    fs,
    path,
    migrationFolder,
  }),
  // WARNING: Only enable in development. Disables timestamp-ordering
  // validation, which can cause schema drift between environments.
  // allowUnorderedMigrations: true,
})

const { error, results } = await migrator.migrateToLatest()

results?.forEach((it) => {
  if (it.status === 'Success') {
    console.log(`migration "${it.migrationName}" executed successfully`)
  } else if (it.status === 'Error') {
    console.error(`failed to execute migration "${it.migrationName}"`)
  }
})

if (error) {
  console.error('migration failed', error)
  process.exit(1)
}
```

## Alembic (Python)

### Workflow

```bash
# Generate migration from SQLAlchemy model changes
alembic revision --autogenerate -m "add user avatar"

# Handwritten migration (custom SQL, data backfill)
alembic revision -m "backfill display names"

# Apply pending migrations
alembic upgrade head

# Inspect state
alembic current
alembic history

# Rollback last migration (dev only — production rollbacks are new forward migrations)
alembic downgrade -1
```

### Autogenerate Pitfalls

Autogenerate diffs SQLAlchemy metadata against the live database — always review the generated file. It misses several change types:

- **Renames**: a renamed table or column is emitted as drop + add, which destroys data if applied blindly. Rewrite by hand as `op.rename_table(...)` / `op.alter_column(..., new_column_name=...)`.
- **Server defaults**: not compared unless `compare_server_default=True` is set in `context.configure()` (in `env.py`).
- **Postgres ENUM value changes**: adding a member to an existing enum type is not detected — write `op.execute("ALTER TYPE ... ADD VALUE ...")` manually.
- **Objects outside table metadata**: views, triggers, functions, and stored procedures are invisible to autogenerate.

### CREATE INDEX CONCURRENTLY

`CONCURRENTLY` cannot run inside a transaction, and Alembic runs the whole upgrade in one by default. Use an autocommit block:

```python
def upgrade():
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email)"
        )

def downgrade():
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_users_email")
```

### down_revision Discipline

Migrations form a chain via `down_revision`. Two branches that each add a migration produce multiple heads, and `alembic upgrade head` refuses to run until resolved.

- After every merge/rebase, check `alembic heads` — expect exactly one head.
- Resolve divergence with a merge revision: `alembic merge heads -m "merge branches"`.
- Never edit the `down_revision` of a migration that has run in production — create new revisions instead.

## Zero-Downtime Migration Strategy

For critical production changes, follow the expand-contract pattern:

```
Phase 1: EXPAND
  - Add new column/table (nullable or with default)
  - Deploy: app writes to BOTH old and new
  - Backfill existing data

Phase 2: MIGRATE
  - Deploy: app reads from NEW, writes to BOTH
  - Verify data consistency

Phase 3: CONTRACT
  - Deploy: app only uses NEW
  - Drop old column/table in separate migration
```

### Timeline Example

```
Day 1: Migration adds new_status column (nullable)
Day 1: Deploy app v2 — writes to both status and new_status
Day 2: Run backfill migration for existing rows
Day 3: Deploy app v3 — reads from new_status only
Day 7: Migration drops old status column
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Manual SQL in production | No audit trail, unrepeatable | Always use migration files |
| Editing deployed migrations | Causes drift between environments | Create new migration instead |
| NOT NULL without default | Fails outright on a non-empty table | Add nullable, backfill, then NOT VALID → VALIDATE → SET NOT NULL |
| Volatile default (`gen_random_uuid()`, `random()`, `clock_timestamp()`) | Rewrites the whole table under ACCESS EXCLUSIVE | Add nullable, backfill in batches, then set the default |
| `DEFAULT now()` on an existing table | `now()` is STABLE, so there is no rewrite — but every existing row is stamped with the *same* backfill timestamp | Fine if that is what you want; otherwise add nullable and backfill from a real event time |
| `ALTER TABLE` with no `lock_timeout` | Lock queue stalls all traffic behind one long query | `SET lock_timeout` and retry with backoff |
| Inline index on large table | Blocks writes during build | CREATE INDEX CONCURRENTLY |
| Schema + data in one migration | Hard to rollback, long transactions | Separate migrations |
| Dropping column before removing code | Application errors on missing column | Remove code first, drop column next deploy |

## Appendix: PostgreSQL Quick Reference

Query optimization, schema design, and security patterns for day-to-day PostgreSQL work.

### Index Selection

| Query Pattern | Index Type | Example |
|--------------|------------|---------|
| `WHERE col = value` / `WHERE col > value` | B-tree (default) | `CREATE INDEX idx ON t (col)` |
| `WHERE a = x AND b > y` | Composite — equality columns first, then range | `CREATE INDEX idx ON t (a, b)` |
| `WHERE jsonb @> '{}'` / full-text `tsv @@ query` | GIN | `CREATE INDEX idx ON t USING gin (col)` |
| Time-series ranges | BRIN | `CREATE INDEX idx ON t USING brin (col)` |

```sql
-- Covering index: avoids table lookup for SELECT email, name, created_at
CREATE INDEX idx ON users (email) INCLUDE (name, created_at);

-- Partial index: smaller, only indexes active rows
CREATE INDEX idx ON users (email) WHERE deleted_at IS NULL;
```

### Data Types

| Use Case | Correct Type | Avoid |
|----------|-------------|-------|
| IDs | `bigint` | `int`, random UUID |
| Strings | `text` | `varchar(255)` |
| Timestamps | `timestamptz` | `timestamp` |
| Money | `numeric(10,2)` | `float` |
| Flags | `boolean` | `varchar`, `int` |

### Query Patterns

```sql
-- UPSERT
INSERT INTO settings (user_id, key, value)
VALUES (123, 'theme', 'dark')
ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value;

-- Cursor pagination: O(1) vs OFFSET's O(n)
SELECT * FROM products WHERE id > $last_id ORDER BY id LIMIT 20;

-- Queue processing without lock contention
UPDATE jobs SET status = 'processing'
WHERE id = (
  SELECT id FROM jobs WHERE status = 'pending'
  ORDER BY created_at LIMIT 1
  FOR UPDATE SKIP LOCKED
) RETURNING *;
```

### Row Level Security

```sql
-- Wrap the auth function in SELECT so it's evaluated once, not per row
CREATE POLICY policy ON orders
  USING ((SELECT auth.uid()) = user_id);
```

### Diagnostics

```sql
-- Slow queries (requires pg_stat_statements)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC;

-- Table bloat
SELECT relname, n_dead_tup, last_vacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Unindexed foreign keys
SELECT conrelid::regclass, a.attname
FROM pg_constraint c
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
WHERE c.contype = 'f'
  AND NOT EXISTS (
    SELECT 1 FROM pg_index i
    WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );
```

### Configuration and Security Defaults

```sql
ALTER SYSTEM SET max_connections = 100;         -- adjust for RAM
ALTER SYSTEM SET work_mem = '8MB';
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '30s';
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
REVOKE ALL ON SCHEMA public FROM public;        -- lock down public schema
SELECT pg_reload_conf();
```

---

*Appendix based on Supabase Agent Skills (credit: Supabase team) (MIT License)*
