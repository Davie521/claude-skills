---
name: setup-opencli
description: >-
  Install, connect and troubleshoot OpenCLI (@jackwener/opencli), the CLI that
  drives the user's own logged-in Chrome so an agent can read sites like
  Xiaohongshu, Twitter/X, Reddit, Bilibili, Zhihu, Weibo, Taobao and 100+ more
  without API keys. Use when the user mentions OpenCLI or asks to install or set
  it up; when a task needs content from a site behind the user's login (or
  clicking through their real Chrome) and opencli is not installed or not
  connected yet; when an opencli command fails with "command not found",
  BROWSER_CONNECT, a disconnected extension or "attach failed"; or before
  upgrading opencli or relaying its "Update available" notice (a plain upgrade
  can silently delete locally edited adapters). Walks Node, npm package, Chrome
  extension and login, verifying each step, then hands off to OpenCLI's own
  bundled skills. Not for plain public web search (use search-routing).
---

# Setup OpenCLI

OpenCLI turns websites into CLI commands by borrowing the user's live Chrome
session — no API keys, no second login. Three moving parts:

1. the npm package (`opencli` binary)
2. a local daemon it starts on demand (`127.0.0.1:19825`)
3. the **OpenCLI Chrome extension**, which lets the daemon drive Chrome

This skill gets all three working and verified, then gets out of the way.
Day-to-day usage is documented by the skills OpenCLI ships with itself
(`opencli skills list`); those track the installed version, so don't restate
them here.

Upstream recommends its desktop app, **OpenCLIApp**, for macOS / Windows desktop
use, and the npm package for CLI-only setups. This skill automates the npm route,
which suits Claude Code users and is the one verified here. If the user prefers
the app, point them to the download link in OpenCLI's README
(https://github.com/jackwener/OpenCLI), then continue at §4.

Verified on macOS with Google Chrome. On Linux / Windows the flow is the same but
the commands for opening Chrome and checking processes differ; other Chromium
browsers aren't covered. Say so rather than guessing.

Talk to the user in the language they wrote in, even though this skill is in
English; keep commands and error strings verbatim.

## 0. Where are we?

```bash
command -v opencli && opencli doctor
```

Read the **whole** doctor output, including `Issues:` — it usually names the
fix. Healthy means all three: `[OK] Daemon`, `[OK] Extension`,
`[OK] Connectivity`. An `Issues:` entry that only lists local adapter overrides
is informational; follow any other issue's own instructions.

- Healthy → run `opencli skills read opencli-usage` (once per session), then do
  the user's task. Stop reading this skill.
- `opencli` not found → §1.
- `opencli` found, not healthy, and the extension has **never** connected on
  this machine (`[MISSING] Extension` and `opencli profile list` shows no
  profiles) → §1 first — the consent is about the extension — then §4. Skip the
  npm items in §1.
- `opencli` found, not healthy, but it has worked before → §4 troubleshooting.
- The user wants to upgrade, or opencli printed `Update available` → read
  `${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` § Upgrades
  and check `opencli adapter status` **before** suggesting any `npm install -g`
  command. Don't pass the notice's bare command along unchecked.

## 1. Check Chrome, explain, then ask — before installing anything

First confirm Google Chrome is installed:

```bash
/bin/ls -d "/Applications/Google Chrome.app" "$HOME/Applications/Google Chrome.app" 2>/dev/null || true
```

No output → tell the user this setup needs Google Chrome and stop until they
have it.

It is the user's machine. Before the first install command, say in plain words
what will happen and **wait for an explicit yes**:

- a global npm package, `@jackwener/opencli` (open source:
  https://github.com/jackwener/OpenCLI)
- the OpenCLI Chrome extension from the Chrome Web Store, which they add with one
  click. It asks for `debugger`, `cookies` and `tabs` access on all sites; while
  it drives a tab, Chrome shows a "started debugging this browser" bar — that is
  expected. With Chrome Sync on, the extension can also appear on their other
  computers (inert there without the daemon).
- **the trade-off:** the daemon listens on `127.0.0.1:19825` with no per-user
  password. While Chrome is open with the extension connected, **any program on
  this computer — including programs run by other accounts on a shared Mac — can
  ask it to drive Chrome with the user's logins and read their cookies for any
  site.** That is how OpenCLI works. Usually fine on a personal machine; think
  twice on a shared one.
- **undo:** `opencli daemon stop` → remove the extension at
  `chrome://extensions` → `npm rm -g @jackwener/opencli`. Optionally delete
  `~/.opencli` (config, edited adapters, a `spotify.env` credentials template)
  and the shell completion file the install printed (zsh:
  `~/.zsh/completions/_opencli`).

In the same message, ask which site they want to use first — §5 needs it.

No yes → stop and offer public-web alternatives instead. An earlier "install it
for me" counts as the yes only if they have already heard the trade-off.

## 2. Node

```bash
node -v
```

The npm package and OpenCLI's README require Node ≥ 20; the bundled
`opencli-usage` skill says ≥ 21. The current LTS (22 or newer) satisfies both.

- Missing or too old → ask before installing one. Prefer a user-level version
  manager — **fnm** or **nvm** — or `brew install node`; with these, global npm
  installs work without root. Avoid the nodejs.org `.pkg` installer: it puts
  npm's global directory under root, so §3 then fails with `EACCES`.
- Never fix permission errors with `sudo npm` (see §3).

**Your own shell won't see a new `PATH`.** Claude Code fixes each Bash call's
environment when the session starts, so editing an rc file (or `fnm`/`nvm`
setup) doesn't reach you until the user restarts Claude Code. Until then, call
new binaries by absolute path, or prefix each command, e.g.
`export PATH="<bin dir>:$PATH"; node -v`. Get the bin dir from the tool:
`fnm exec --using=22 which node`, or `. ~/.nvm/nvm.sh && nvm which 22` (strip the
trailing `/node`). Tell the user their own terminals pick it up once the rc file
is updated.

## 3. Install the package

```bash
npm install -g @jackwener/opencli
opencli --version   # or "$(npm prefix -g)/bin/opencli" --version, see §2
```

- `EACCES` → npm's global directory is root-owned. Don't `sudo`. Switch to a
  user-level Node (§2), or — after asking, since it changes npm's global config —
  `npm config set prefix ~/.npm-global`, put `~/.npm-global/bin` on `PATH`, and
  retry.
- Installed but `opencli: command not found` → the global bin dir isn't on
  `PATH`: `npm prefix -g` gives the prefix, the binary is in `<prefix>/bin`. Use
  the absolute path in this session (§2) and tell the user which rc file to add
  it to.

The install's postinstall step writes shell completion (and prints how to
enable it), creates `~/.opencli/` with a `spotify.env` template, and prints
instructions to download the extension from GitHub releases and **Load
unpacked**. Ignore that last part: use the Chrome Web Store in §4 — it updates
itself. Upgrades are different from a first install — read
`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` § Upgrades
before ever upgrading.

## 4. Chrome extension

1. Open the store page **in Chrome**, not the default browser (often Safari):

   ```bash
   open -a "Google Chrome" "https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk"
   ```

2. Ask the user to click **Add to Chrome** → **Add extension**. You cannot do
   this click: Chrome does not let programs install extensions silently.
3. Install it in the Chrome profile where they are logged in to the sites they
   care about; if the page opened in another profile, switch first. It can live
   in several profiles — OpenCLI then needs a default (see the table).
4. Verify with `opencli doctor` → `[OK] Extension`.

### Extension stays disconnected

Read doctor's `Issues:` first. Then work down the table, re-running
`opencli doctor` after each fix.

| Check | How | Fix |
|---|---|---|
| Chrome running? | `pgrep -x "Google Chrome"` | `open -ga "Google Chrome"`, wait ~5 s |
| Which profile has it, is it enabled, is that profile open? | profile script below | `wrong_profile_open` → `open -na "Google Chrome" --args --profile-directory="<openThisProfile>"`; `installed_but_disabled` → user turns it on at `chrome://extensions`; `not_installed` → back to step 1 |
| Several profiles connected | doctor / `opencli daemon status` says `profiles connected, none selected` or `requested profile not connected` | `opencli profile list`, then `opencli profile use <name>` |
| Daemon older than the CLI | doctor: `Stale daemon detected` | `opencli daemon restart` |
| Daemon just restarted | — | the extension needs a few seconds to reconnect: poll `opencli daemon status` for `Extension: connected`, up to ~30 s |
| Still disconnected after `opencli daemon restart` twice | — | the extension's background worker is stuck: quit and reopen Chrome. **Ask first** — it closes their tabs; note the open URLs |

Profile script (read-only; reads Chrome's `Local State` and each profile's
preference files, prints JSON):

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/scripts/find-extension-profile.mjs"
```

It finds both the Web Store install and an unpacked one (`installs[].kind`).
`chrome_not_found` (exit 2) means Chrome has never been run or isn't Google
Chrome; `local_state_unreadable` (exit 3) means Chrome's own state file didn't
parse — ask the user to look at `chrome://extensions` instead. `enabled: null`
means Chrome left no readable setting: unknown, not disabled. `inUse` is the
profiles Chrome last had open and can lag while Chrome runs, so when the verdict
and what the user sees disagree, believe the user. `multipleProfiles: true` →
expect the "none selected" row above.

## 5. Log in, then prove it with real data

`[OK] Connectivity` proves the bridge, not that a site works.

1. The user logs in to the target site in that Chrome profile. Never type their
   password or solve a CAPTCHA for them.
2. List the site's commands: `opencli <site> --help -f yaml`. Each has `access`
   (`read` / `write`) and `browser` (`true` = needs the extension). Don't infer
   browser needs from `strategy`, and don't dump `opencli list -f json` into the
   conversation — it is over a megabyte.
3. Run one small command with `access: read` and `browser: true` that only
   returns real content when logged in (a feed, saved items, history). **Never use
   an `access: write` command as a test** — those post, follow, comment or
   change account state. Real rows → done.

An auth error means not logged in. The reverse also happens: sites keep
nickname / avatar cookies after the session expires, so the browser *looks*
logged in. When unsure, have the user open a page that requires login (orders,
bookmarks) and check whether it shows a login button.

Finish with a short report: what was installed, which Chrome profile holds the
extension, which site was verified and by which command.

## 6. Hand off

OpenCLI's bundled skills are the reference from here on:

```bash
opencli skills list
opencli skills read opencli-usage     # start here: discovery, flags, output formats
opencli skills read opencli-browser   # driving the browser directly
opencli skills read opencli-autofix   # an adapter command broke
```

Read `opencli-usage` before the first real task. If the user wants those skills
to load automatically, upstream's way is `npx skills add jackwener/opencli` —
another install, so ask first.
`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` covers
failure modes the bundled skills don't: upgrades deleting edited adapters,
sessions losing their tab, uploads, rate limits.

## Never

- install anything before the user's yes in §1
- `sudo npm install -g`
- type the user's passwords or solve CAPTCHAs for them
- run an `access: write` command to test a setup
- keep hitting a site after a CAPTCHA or "too many requests" — stop and tell the
  user (`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md`
  § Rate limits)
