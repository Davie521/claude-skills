---
description: Restate requirements, assess risks, and create step-by-step implementation plan. WAIT for user CONFIRM before touching any code.
---

# Plan Command

This command invokes the **planner** agent to create a comprehensive implementation plan before writing any code.

## What This Command Does

1. **Restate Requirements** - Clarify what needs to be built
2. **Identify Risks** - Surface potential issues and blockers
3. **Create Step Plan** - Break down implementation into phases
4. **Wait for Confirmation** - MUST receive user approval before proceeding
5. **Create Worktree** - After confirmation, set up an isolated git worktree before any coding

## When to Use

Use `/plan` when:
- Starting a new feature
- Making significant architectural changes
- Working on complex refactoring
- Multiple files/components will be affected
- Requirements are unclear or ambiguous

## How It Works

The planner agent will:

1. **Analyze the request** and restate requirements in clear terms
2. **Break down into phases** with specific, actionable steps
3. **Identify dependencies** between components
4. **Assess risks** and potential blockers
5. **Estimate complexity** (High/Medium/Low)
6. **Present the plan** and WAIT for your explicit confirmation

## Example Usage

```
User: /plan I need to add real-time notifications when markets resolve

Agent (planner):
# Implementation Plan: Real-Time Market Resolution Notifications

## Requirements Restatement
- Send notifications to users when markets they're watching resolve
- Support multiple notification channels (in-app, email, webhook)
- Ensure notifications are delivered reliably
- Include market outcome and user's position result

## Implementation Phases

### Phase 1: Database Schema
- Add notifications table with columns: id, user_id, market_id, type, status, created_at
- Add user_notification_preferences table for channel preferences
- Create indexes on user_id and market_id for performance

### Phase 2: Notification Service
- Create notification service in lib/notifications.ts
- Implement notification queue using BullMQ/Redis
- Add retry logic for failed deliveries
- Create notification templates

### Phase 3: Integration Points
- Hook into market resolution logic (when status changes to "resolved")
- Query all users with positions in market
- Enqueue notifications for each user

### Phase 4: Frontend Components
- Create NotificationBell component in header
- Add NotificationList modal
- Implement real-time updates via Supabase subscriptions
- Add notification preferences page

## Dependencies
- Redis (for queue)
- Email service (SendGrid/Resend)
- Supabase real-time subscriptions

## Risks
- HIGH: Email deliverability (SPF/DKIM required)
- MEDIUM: Performance with 1000+ users per market
- MEDIUM: Notification spam if markets resolve frequently
- LOW: Real-time subscription overhead

## Estimated Complexity: MEDIUM
- Backend: 4-6 hours
- Frontend: 3-4 hours
- Testing: 2-3 hours
- Total: 9-13 hours

**WAITING FOR CONFIRMATION**: Proceed with this plan? (yes/no/modify)
```

## Important Notes

**CRITICAL**: The planner agent will **NOT** write any code until you explicitly confirm the plan with "yes" or "proceed" or similar affirmative response.

If you want changes, respond with:
- "modify: [your changes]"
- "different approach: [alternative]"
- "skip phase 2 and do phase 3 first"

## Worktree Setup After Confirmation (REQUIRED)

After the user explicitly confirms the plan (e.g. "yes", "proceed", "go") and BEFORE writing any code, set up an isolated git worktree:

1. **Derive the worktree name from `$ARGUMENTS`:**
   - Slugify: lowercase, replace whitespace and punctuation with `-`, collapse repeats, strip leading/trailing `-`, truncate to ~40 chars.
   - If `$ARGUMENTS` is non-ASCII (e.g. Chinese), translate the gist to a short English slug instead of transliterating.
   - Prefix with `plan-`. Example: `add podcast feature` → `plan-add-podcast-feature`.

2. **Ensure we're inside a git repo:**
   Run `git rev-parse --is-inside-work-tree` in the current working directory. If it fails (not a git repo), run `git init` first — do not skip this step.

3. **Sync the latest main:**
   If the repo has a remote, run `git fetch origin` first. Detect the default branch name with `git symbolic-ref --short refs/remotes/origin/HEAD` (typically `origin/main`, sometimes `origin/master`). This is the **base ref** for the new worktree — always branch off the latest main, never off the current HEAD or a feature branch.

4. **Create the worktree** branching off the latest main. Prefer the `EnterWorktree` tool with the base ref set to that main. If unavailable, fall back to `git worktree add ../<name> -b <name> origin/<default-branch>`. (For a freshly `git init`-ed repo with no remote, use the local default branch's HEAD as the base.)

5. **Announce the worktree path and base ref** to the user (e.g. "created worktree at `../plan-add-podcast` branched off `origin/main` @ abc1234"), then perform all subsequent code changes inside it.

## Integration with Other Commands

After planning:
- Use `/tdd` to implement with test-driven development
- Use `/build-fix` if build errors occur
- Use `/code-review` to review completed implementation

## Related Agents

This command invokes the `planner` agent provided by ECC.

For manual installs, the source file lives at:
`agents/planner.md`
