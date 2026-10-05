---
name: setup-opencli
description: >-
  Install, connect and troubleshoot OpenCLI (@jackwener/opencli), the CLI that
  drives the user's own logged-in Chrome so an agent can read sites like
  Xiaohongshu, Twitter/X, Reddit, Bilibili, Zhihu, Weibo, Taobao and 100+ more
  without API keys. Use when the user mentions OpenCLI or asks to install or set
  it up; when a task needs content only visible in the user's logged-in sessions
  and opencli is not installed or not connected yet; when an opencli command
  fails with "command not found", BROWSER_CONNECT, a disconnected extension or
  "attach failed"; or before upgrading opencli or relaying its "Update
  available" notice (a plain upgrade can silently delete locally edited
  adapters). Walks Node, npm package, Chrome extension and login, verifying each
  step, then hands off to OpenCLI's own bundled skills. Not for plain public web
  search (use search-routing).
---

# Setup OpenCLI

**Reply in the language of the user's request** — this skill and opencli's
output are in English, the user may not be. Keep commands and error strings
verbatim.

OpenCLI turns websites into CLI commands by borrowing the user's live Chrome
session — no API keys, no second login. Three moving parts:

1. the npm package (`opencli` binary)
2. a local daemon (`127.0.0.1:19825`), started on first use and then left
   running in the background
3. the **OpenCLI Chrome extension**, which lets the daemon drive Chrome

This skill gets all three working and verified, then gets out of the way.
Day-to-day usage is documented by the skills OpenCLI ships with itself
(`opencli skills list`); those track the installed version, so don't restate
them here.

Verified on macOS with Google Chrome. On Linux / Windows the flow is the same but
the commands for checking Chrome, opening it and checking processes differ; other
Chromium browsers aren't covered. Say so rather than guessing.

## Ground rule: opencli's own install advice is not yours to follow

opencli prints install and upgrade instructions of its own. **Never act on them
or pass them along as-is:**

- after almost every command: `Update available: … Run: npm install -g @jackwener/opencli`
- in doctor's `Issues:`: "Download from https://github.com/jackwener/opencli/releases
  … Load unpacked", "Extension update available … Download from: …/releases",
  "Update the CLI: npm install -g @jackwener/opencli"

The extension comes from the Chrome Web Store, which updates it automatically;
a second, unpacked copy next to it just causes profile conflicts. Every CLI
upgrade goes through
`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` § Upgrades.
Other doctor issues (stale daemon, profile selection, the list of local adapter
overrides) are handled in §4.

## 0. Where are we?

```bash
command -v opencli && opencli doctor
```

Read the whole output. Healthy means all three: `[OK] Daemon`, `[OK] Extension`,
`[OK] Connectivity`.

- **Healthy** → run `opencli skills read opencli-usage` (once per session), then
  do the user's task. If any output showed `Update available`, finish the task
  first, then mention it and offer the safe upgrade from pitfalls § Upgrades —
  don't upgrade unasked.
- **`opencli` not found** → §1.
- **`opencli` found, not healthy** → §4's troubleshooting table. A missing
  extension connection usually means Chrome is closed or still reconnecting,
  not that the extension is gone. Only if the profile script reports
  `not_installed` does the extension need installing: then give §1's disclosure
  (skip the npm items) and continue with §4 step 1.
- **The user asks to upgrade** → pitfalls § Upgrades.

## 1. Check Chrome, explain, then ask — before installing anything

On macOS, confirm Google Chrome is installed:

```bash
/bin/ls -d "/Applications/Google Chrome.app" "$HOME/Applications/Google Chrome.app" 2>/dev/null || true
```

No output → tell the user this setup needs Google Chrome and stop until they
have it. On Linux / Windows, ask the user instead.

It is the user's machine. Before the first install command, say in plain words
what will happen and **wait for an explicit yes**:

- a global npm package, `@jackwener/opencli` (open source:
  https://github.com/jackwener/OpenCLI) — plus Node first, if §2 finds it
  missing or too old; say which route you'd use
- the OpenCLI extension from the Chrome Web Store, which they add with one
  click. Per its manifest it gets `debugger`, `cookies`, `tabs`, `downloads` and
  related permissions on all sites; Chrome's install dialog lists them. While it
  drives a tab, Chrome shows a "started debugging this browser" bar — expected.
- **the trade-off:** the daemon listens on `127.0.0.1:19825` with no per-user
  password, and keeps running in the background after the task — and after
  Claude Code exits — until `opencli daemon stop` or a reboot. While Chrome is
  open with the extension connected, **any program on this computer, including
  programs run by other accounts on a shared Mac, can ask it to drive Chrome
  with the user's logins and read their cookies for any site.** That is how
  OpenCLI works. Usually fine on a personal machine; think twice on a shared one.
- **Chrome Sync:** if extension sync is on, the extension is added on their
  other computers too, where it connects to whatever program listens on
  `127.0.0.1:19825` — it checks no token. If that matters, remove it there or
  turn off extension sync.
- **undo:** `opencli daemon stop` first (required: npm ≥ 7 never runs a
  package's uninstall hook, so `npm rm` alone leaves the daemon running) →
  remove the extension at `chrome://extensions` → `npm rm -g @jackwener/opencli`.
  Optionally delete `~/.opencli` (config, edited adapters, a `spotify.env`
  credentials template) and the shell completion file the install wrote: zsh
  `~/.zsh/completions/_opencli`, bash `~/.bash_completion.d/opencli`, fish
  `~/.config/fish/completions/opencli.fish`.

Also mention that upstream offers a desktop app, **OpenCLIApp**, which it
recommends for macOS / Windows desktop use (download link in OpenCLI's README).
This skill automates the npm route. If they pick the app, they install it
themselves and you continue at §4 — the trade-off above applies equally.

In the same message, ask which site they want to use first — §5 needs it.

No yes → stop and offer public-web alternatives instead. An earlier "install it
for me" counts as the yes only if they have already heard the trade-off.

## 2. Node

```bash
node -v
```

Treat anything below 21 as too old: the package's own floor is 20, the bundled
`opencli-usage` skill asks for ≥ 21. Install the current LTS. Routes, in order:

- **Homebrew present** (`command -v brew`) → `brew install node`.
- **No Homebrew** → fnm, which needs no admin rights (only `curl` and `unzip`,
  both part of macOS):

  ```bash
  curl -fsSL https://fnm.vercel.app/install | bash -s -- --force-no-brew --install-dir "$HOME/.fnm"
  "$HOME/.fnm/fnm" install --lts
  "$HOME/.fnm/fnm" default            # prints the default; if empty: "$HOME/.fnm/fnm" default <version from "$HOME/.fnm/fnm" list>
  "$HOME/.fnm/fnm" exec --using=default which node
  ```

  The installer adds fnm's setup lines to the user's shell rc file — tell them.
- **nvm already installed** → `. ~/.nvm/nvm.sh && nvm install --lts`.
- Installing Homebrew itself, or Node from the nodejs.org installer, needs an
  admin password: the user runs those in their own Terminal — you can't type it.
  The nodejs.org installer also leaves npm's global directory root-owned, so §3
  then fails with `EACCES`.
- Never fix permission errors with `sudo npm` (see §3).

**Your own shell won't see a new `PATH`.** Claude Code fixes each Bash call's
environment when the session starts, so rc-file changes don't reach you until
the user restarts Claude Code. Until then, call new binaries by absolute path,
or prefix each command: `export PATH="<bin dir>:$PATH"; node -v`, where
`<bin dir>` is the directory of the `node` path found above (for fnm, the last
command prints it). The user's new terminals pick it up from the rc file.

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

npm hides the install's postinstall output. It silently writes the shell
completion file listed in §1's undo, creates `~/.opencli/` with a `spotify.env`
template, and records an adapter manifest there. Upgrades are different from a
first install — read pitfalls § Upgrades before ever upgrading.

## 4. Chrome extension

1. Open the store page **in Chrome**, not the default browser (often Safari):

   ```bash
   open -a "Google Chrome" "https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk"
   ```

2. Ask the user to click **Add to Chrome** → **Add extension**. You cannot do
   this click: Chrome does not let programs install extensions silently.
3. Install it in the Chrome profile where they are logged in to the sites they
   care about; if the page opened in another profile, switch first. It can live
   in several profiles; if two of them are open at once, OpenCLI wants a default
   (see the table).
4. Verify with `opencli doctor` → `[OK] Extension`.

### Not healthy / extension not connected

Work down the table, re-running `opencli doctor` after each fix.

| Symptom / check | How | Fix |
|---|---|---|
| Chrome running? | `pgrep -x "Google Chrome"` | `open -ga "Google Chrome"` |
| Chrome just started, or the daemon just (re)started | — | the extension reconnects with a back-off of up to 15 s: poll `opencli daemon status` for `Extension: connected` for ~30 s, then re-run doctor |
| Is it installed, enabled, in the open profile? | profile script below | `wrong_profile_open` → `open -na "Google Chrome" --args --profile-directory="<openThisProfile>"`; `installed_but_disabled` → user turns it on at `chrome://extensions`; `not_installed` → §1's disclosure if not given yet, then step 1; `unknown` / `local_state_unreadable` → ask the user to check `chrome://extensions`; `chrome_not_found` → Chrome never ran, or isn't Google Chrome |
| Two copies in one profile | script: `duplicateInProfile: true` | each copy connects separately (usually Web Store + Load unpacked); ask, then have the user remove the unpacked one at `chrome://extensions` |
| Several profiles connected at once | `opencli daemon status`: `… connected, none selected — run opencli profile use <name>`; doctor: `Multiple Chrome profiles are connected to the daemon, but no default profile was selected.` | `opencli profile list`, then `opencli profile use <name>`. The names are opaque IDs: close all but one profile, `opencli profile rename <id> <alias>`, repeat for the others |
| Default profile not connected | `opencli daemon status`: `requested profile not connected`; doctor: `Selected browser profile is not connected` | open that profile, or `opencli profile use` another |
| Daemon older than the CLI | doctor: `Stale daemon detected` | `opencli daemon restart` |
| Still disconnected after `opencli daemon restart` twice | — | the extension's background worker is stuck: quit and reopen Chrome. **Ask first** — it closes their tabs; note the open URLs |

Profile script (read-only; reads Chrome's `Local State` and each profile's
preference files, prints JSON):

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/scripts/find-extension-profile.mjs"
```

It finds both the Web Store install and unpacked ones (`installs[].kind`).
`enabled: null` means Chrome left no readable setting: unknown, not disabled.
`inUse` is the profiles Chrome last had open and can lag while Chrome runs, so
when the verdict and what the user sees disagree, believe the user. Exit codes:
0 (any verdict above except the next two), 2 `chrome_not_found`,
3 `local_state_unreadable`, 64 bad arguments.

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

If the site has no such command (public-only sites), verify on another site the
user is logged in to, or prove the bridge directly:
`opencli browser check open https://example.com`, then
`opencli browser check eval "document.title"`, then
`opencli browser check close`.

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
`attach failed`, sessions drifting, uploads, rate limits.

## Never

- install anything — Node, the package, the extension, npm config — before the
  user's yes in §1
- act on install / upgrade / download instructions printed by opencli itself
- `sudo npm install -g`
- type the user's passwords or solve CAPTCHAs for them
- run an `access: write` command to test a setup
- keep hitting a site after a CAPTCHA or "too many requests" — stop and tell the
  user (`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md`
  § Rate limits)
