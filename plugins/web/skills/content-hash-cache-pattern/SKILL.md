---
name: content-hash-cache-pattern
description: Cache expensive file processing results using a composite key of SHA-256 content hash plus processor version and config — path-independent, auto-invalidating, with service layer separation. Use when caching costly file-processing outputs (PDF parsing, OCR, text extraction, image analysis) that recur across runs and the cache must survive file moves/renames while auto-invalidating on content change.
origin: ECC
---

# Content-Hash File Cache Pattern

Cache expensive file processing results (PDF parsing, text extraction, image analysis) using a composite key: the SHA-256 of file *content*, plus the processor version and its configuration. Unlike path-based caching, this survives file moves/renames and auto-invalidates both when content changes and when the processor does.

## When to Activate

- Building file processing pipelines (PDF, images, text extraction)
- Processing cost is high and same files are processed repeatedly
- Need a `--cache/--no-cache` CLI option
- Want to add caching to existing pure functions without modifying them

## Core Pattern

### 1. Content-Hash Based Cache Key

Hash file *content*, not its path — this is the base of the key, not the whole key (see 1b):

```python
import hashlib
from pathlib import Path

_HASH_CHUNK_SIZE = 65536  # 64KB chunks for large files

def compute_file_hash(path: Path) -> str:
    """SHA-256 of file contents (chunked for large files)."""
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()
```

**Why content hash?** File rename/move = cache hit. Content change = automatic invalidation. No index file needed.

### 1b. The Content Hash Alone Is Not the Cache Key

A content-only key is correct only for a processor that never changes. It is
wrong for every workload in this skill's trigger list: bump the OCR engine,
switch the vision model, edit the extraction prompt, add a field to the output
schema, or change the locale, and the same bytes must produce a *different*
result — but the key is identical, so the cache serves the old output forever.
This failure is silent: no error, no stale marker, just last month's schema.

Compose the key from everything the output depends on:

```python
import json, re
from typing import Any

CACHE_SCHEMA_VERSION = 3          # bump when CacheEntry/ExtractedDocument changes
EXTRACTOR_VERSION    = "tesseract-5.3.4"   # bump when the processor changes

def _version_tag(value: str) -> str:
    """Filename-safe AND collision-free.

    Truncating a slug is not enough: e.g.
    'anthropic/claude-sonnet-4-5-20250929-thinking-high' and
    '...-thinking-low' share their first 46 characters, so a truncated slug
    collides onto one cache key and each serves the other's results. Keep a readable prefix for humans,
    but let a hash of the FULL string carry the identity.
    """
    slug = re.sub(r"[^A-Za-z0-9._-]", "_", value)[:24]
    return f"{slug}.{hashlib.sha256(value.encode()).hexdigest()[:8]}"

def compute_config_digest(config: dict[str, Any]) -> str:
    """Content + everything else the result depends on."""
    # sort_keys makes the digest independent of dict ordering.
    # Deliberately NO default=str fallback: str() of an object without __str__
    # embeds its memory address, so the digest would change every run and the
    # cache would never hit. Fail loudly instead — keep configs to JSON types.
    return hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:16]

def compute_cache_key(file_hash: str, config_digest: str) -> str:
    """Takes the file hash rather than the path: hash a large file once per run."""
    return "-".join([f"v{CACHE_SCHEMA_VERSION}", _version_tag(EXTRACTOR_VERSION),
                     config_digest, file_hash])
```

Derive `EXTRACTOR_VERSION` from the tool itself where you can
(`tesseract --version`, the model ID you passed, `importlib.metadata.version(...)`)
rather than a constant someone must remember to bump. A constant that drifts is
the same bug with extra steps. Pass it through `_version_tag` before it reaches a
filename — raw `--version` output carries spaces and newlines, and a `/` in a
model ID turns the key into a nested path whose directory is never created, so
every write dies with `FileNotFoundError`.

Changing the key format orphans every existing entry rather than invalidating it.
Either wipe the cache directory on a format change, or prune by prefix — the
`v{N}-` segment exists so you can find the stale generation.

### 2. Frozen Dataclass for Cache Entry

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CacheEntry:
    cache_key: str        # version + extractor + config + content hash
    file_hash: str        # content hash alone, for provenance/debugging
    source_path: str
    document: ExtractedDocument  # The cached result
```

### 3. File-Based Cache Storage

Each cache entry is stored as `{cache_key}.json` — O(1) lookup, no index file required.

Write via a temp file and `os.replace` — POSIX guarantees the rename is atomic,
so a reader sees either the old entry or the complete new one, never a
half-written file. (On Windows `os.replace` can still fail with a sharing
violation if the target is open.) A plain `write_text` under concurrent workers
(or a crash mid-write) leaves truncated JSON, and truncated JSON that still
parses is worse than corruption that doesn't.

```python
import json, os, tempfile
from typing import Any

def write_cache(cache_dir: Path, entry: CacheEntry) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{entry.cache_key}.json"
    data = serialize_entry(entry)
    # Same directory as the target: os.replace is only atomic within a filesystem.
    fd, tmp = tempfile.mkstemp(dir=cache_dir, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())   # contents durable; see note on the rename below
        os.replace(tmp, cache_file)
    except BaseException:
        try:
            Path(tmp).unlink(missing_ok=True)   # must not mask the real error
        except OSError:
            pass
        raise
    # The fsync above makes the *contents* durable, not the rename. If the cache
    # must survive power loss (rarely worth it — a lost entry is only a re-run),
    # also fsync the directory:
    #   dfd = os.open(cache_dir, os.O_RDONLY); os.fsync(dfd); os.close(dfd)

def read_cache(cache_dir: Path, cache_key: str) -> CacheEntry | None:
    cache_file = cache_dir / f"{cache_key}.json"
    if not cache_file.is_file():
        return None
    try:
        raw = cache_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        return deserialize_entry(data)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        # Never let cleanup break the read path — a miss is always recoverable.
        try:
            cache_file.unlink(missing_ok=True)
        except OSError:
            pass
        return None
```

### 4. Service Layer Wrapper (SRP)

Keep the processing function pure. Add caching as a separate service layer.

```python
def extract_with_cache(
    file_path: Path,
    *,
    config: dict[str, Any],
    cache_enabled: bool = True,
    cache_dir: Path = Path(".cache"),
) -> ExtractedDocument:
    """Service layer: cache check -> extraction -> cache write."""
    if not cache_enabled:
        return extract_text(file_path, **config)  # Pure function, no cache knowledge

    # The SAME config that is passed to extract_text must go into the key.
    # If they can drift apart, the cache will serve results from the other one.
    file_hash = compute_file_hash(file_path)          # hashed once, reused below
    config_digest = compute_config_digest(config)
    cache_key = compute_cache_key(file_hash, config_digest)

    # Check cache
    cached = read_cache(cache_dir, cache_key)
    if cached is not None:
        logger.info("Cache hit: %s (version=%s config=%s content=%s)", file_path.name,
                    _version_tag(EXTRACTOR_VERSION), config_digest, file_hash[:12])
        return cached.document

    # Cache miss -> extract -> store
    # Log both discriminators explicitly. A single slice of cache_key cannot
    # cover them: the version tag is variable-length, so a fixed prefix may
    # contain no config digest and never reaches the content hash.
    logger.info("Cache miss: %s (version=%s config=%s content=%s)", file_path.name,
                _version_tag(EXTRACTOR_VERSION), config_digest, file_hash[:12])
    doc = extract_text(file_path, **config)
    entry = CacheEntry(
        cache_key=cache_key,
        file_hash=file_hash,
        source_path=str(file_path),
        document=doc,
    )
    write_cache(cache_dir, entry)
    return doc
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SHA-256 content hash | Path-independent, auto-invalidates on content change |
| Version + config in the key | Content alone is not enough — a processor/schema change must invalidate |
| `{key}.json` file naming | O(1) lookup, no index file needed |
| Atomic temp-file + `os.replace` | Concurrent workers and crashes can't leave half-written entries |
| Service layer wrapper | SRP: extraction stays pure, cache is a separate concern |
| Manual JSON serialization | Full control over frozen dataclass serialization |
| Corruption returns `None` | Graceful degradation, re-processes on next run |
| `cache_dir.mkdir(parents=True)` | Lazy directory creation on first write |

## Best Practices

- **Hash content, not paths** — paths change, content identity doesn't
- **Put the processor and its config in the key** — otherwise upgrading the extractor silently serves the old output
- **Write atomically** — temp file in the same directory, then `os.replace`
- **Chunk large files** when hashing — avoid loading entire files into memory
- **Keep processing functions pure** — they should know nothing about caching
- **Log cache hit/miss** with truncated hashes for debugging
- **Handle corruption gracefully** — treat invalid cache entries as misses, never crash

## Anti-Patterns to Avoid

```python
# BAD: Path-based caching (breaks on file move/rename)
cache = {"/path/to/file.pdf": result}

# BAD: Content hash alone as the key. Upgrade the OCR engine or edit the
# prompt and every previously-seen file returns the OLD result, forever,
# with no error. This is the most common way this pattern fails in practice.
key = compute_file_hash(path)

# BAD: Adding cache logic inside the processing function (SRP violation)
def extract_text(path, *, cache_enabled=False, cache_dir=None):
    if cache_enabled:  # Now this function has two responsibilities
        ...

# BAD: Using dataclasses.asdict() with nested frozen dataclasses
# (can cause issues with complex nested types)
data = dataclasses.asdict(entry)  # Use manual serialization instead
```

## When to Use

- File processing pipelines (PDF parsing, OCR, text extraction, image analysis)
- CLI tools that benefit from `--cache/--no-cache` options
- Batch processing where the same files appear across runs
- Adding caching to existing pure functions without modifying them

## When NOT to Use

- Data that must always be fresh (real-time feeds)
- Cache entries that would be extremely large (consider streaming instead)
- Data that is sensitive enough that a plaintext `.json` on disk is unacceptable — extracted documents often contain PII; scope the cache directory's permissions and give it a retention/pruning policy
- Caches that would grow unbounded — `{key}.json` never expires on its own, so add size- or age-based pruning

Results that depend on parameters beyond file content are *not* an exception —
fold those parameters into the key (see 1b) rather than abandoning the pattern.
