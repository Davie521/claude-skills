---
name: setup-opencli
description: Install, connect and troubleshoot OpenCLI (`@jackwener/opencli`), the CLI that drives the user's own logged-in Chrome so an agent can read sites like Xiaohongshu, Twitter/X, Reddit, Bilibili, Zhihu, Weibo, Taobao and 100+ more without API keys. Use when the user mentions OpenCLI or asks to install / set it up; when a task needs content from a site behind the user's login (or clicking through their real Chrome) and `opencli` is not installed or not connected yet; or when an `opencli` command fails with "command not found", BROWSER_CONNECT, "Extension: disconnected" or "attach failed"; or before upgrading opencli or relaying its "Update available" notice (a plain upgrade can silently delete locally edited adapters). Walks Node → npm package → Chrome extension → login, verifying each step, then hands off to OpenCLI's own bundled skills for everyday use. Not for plain public web search (use search-routing).
---

# Setup OpenCLI

OpenCLI turns websites into CLI commands by borrowing the user's live Chrome
session — no API keys, no second login. Three moving parts:

1. the npm package (`opencli` binary)
2. a local daemon it starts on demand (port 19825)
3. the **OpenCLI Chrome extension**, which lets the daemon drive Chrome

This skill gets all three working and verified, then gets out of the way.
Day-to-day usage is documented by the skills OpenCLI ships with itself
(`opencli skills list`); those track the installed version, so don't restate
them here.

Verified on macOS. On Linux / Windows the flow is the same but the commands for
opening Chrome and checking processes differ — tell the user that rather than
guessing.

Talk to the user in the language they wrote in, even though this skill is in
English; keep commands and error strings verbatim.

## 0. Already working? Skip setup

```bash
command -v opencli && opencli doctor
```

Healthy means all three lines are present: `[OK] Daemon`, `[OK] Extension`,
`[OK] Connectivity`. An `Issues:` block listing local adapter overrides is
informational.

- Healthy → run `opencli skills read opencli-usage` (once per session), then do
  the user's task. Stop reading this skill.
- `opencli` exists but doctor is not healthy → go to §4.
- `opencli` not found → §1.
- The user wants to upgrade, or opencli printed `Update available` → read
  `${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` § Upgrades
  and check `opencli adapter status` **before** suggesting any `npm install -g`
  command. Don't pass the notice's bare command along unchecked.

## 1. Explain, then ask — before installing anything

It is the user's machine. Before the first install command, say in plain words
what will happen and **wait for an explicit yes**:

- a global npm package, `@jackwener/opencli` (open source:
  https://github.com/jackwener/OpenCLI)
- a Chrome extension from the Chrome Web Store, which they add with one click
- **the trade-off:** once connected, any program running as this user can ask
  the local daemon to drive their Chrome *with their logins*. That is how
  OpenCLI works. Fine on a personal machine; worth knowing on a shared one.
  Undo = remove the extension and `npm rm -g @jackwener/opencli`.

In the same message, ask which site they want to use first — §5 needs it.

No yes → stop and offer public-web alternatives instead. An earlier "install it
for me" counts as the yes only if they have already heard the trade-off.

## 2. Node

```bash
node -v
```

The package declares Node ≥ 20 and OpenCLI's own docs say ≥ 21; the current LTS
(22 or newer) satisfies both.

- Missing or too old → ask before installing one. Prefer a user-level version
  manager (fnm, nvm) or the installer from nodejs.org; `brew install node` also
  works on macOS.
- Never fix permission errors with `sudo npm` (see §3).

## 3. Install the package

```bash
npm install -g @jackwener/opencli
opencli --version
```

- `EACCES` → npm's global prefix is a root-owned system directory. Don't `sudo`.
  Use a user-level Node (fnm / nvm), or set a user prefix
  (`npm config set prefix ~/.npm-global`, add `~/.npm-global/bin` to `PATH`) and
  retry.
- Installed but `opencli: command not found` → the global bin dir is not on
  `PATH`. `npm prefix -g` gives the prefix; the binary is in `<prefix>/bin`. Tell
  the user which shell rc file to add it to; a new terminal picks it up.

A plain install is right the first time: its postinstall only writes shell
completion and an adapter manifest. Upgrades are different — read
`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` § Upgrades before ever upgrading.

## 4. Chrome extension

Requires Google Chrome.

1. Open the store page **in Chrome**, not the default browser (often Safari):

   ```bash
   open -a "Google Chrome" "https://chromewebstore.google.com/detail/opencli/ildkmabpimmkaediidaifkhjpohdnifk"
   ```

2. Ask the user to click **Add to Chrome** → **Add extension**. You cannot do
   this click: Chrome does not let programs install extensions silently.
3. The extension lives in **one Chrome profile**. Tell the user to add it in the
   profile where they are logged in to the sites they care about; if the page
   opened in another profile, switch profiles first.
4. Verify with `opencli doctor` → `[OK] Extension`.

### Extension stays disconnected

Work down the table; re-run `opencli doctor` after each fix.

| Check | How | Fix |
|---|---|---|
| Chrome running? | `pgrep -x "Google Chrome"` | `open -ga "Google Chrome"`, wait ~5 s |
| Extension in the profile that is open? | run the profile script below | `verdict: wrong_profile_open` → `open -na "Google Chrome" --args --profile-directory="<openThisProfile>"` |
| Extension disabled? | same script, `installed_but_disabled` | user turns it on at `chrome://extensions` |
| Not installed after all? | same script, `not_installed` | back to step 1 |
| Daemon just restarted? | — | the extension needs a few seconds to reconnect; wait, retry once |
| Still disconnected after `opencli daemon restart` twice | — | the extension's background worker is stuck: quit and reopen Chrome. **Ask first** — it closes their tabs; note the open URLs |

Profile script (read-only; reads Chrome's `Local State` and per-profile
preferences, prints JSON):

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/scripts/find-extension-profile.mjs"
```

`profiles[].enabled` is `null` when Chrome left no readable setting — treat that
as unknown, not disabled. `lastActive` is the profiles Chrome most recently had
open; it can lag while Chrome is running, so when the verdict and what the user
sees disagree, believe the user.

## 5. Log in, then prove it with real data

`[OK] Connectivity` proves the bridge, not that a site works.

1. The user logs in to the target site in that Chrome profile. Never type their
   password or solve a CAPTCHA for them.
2. Find commands for the site: `opencli list -f json`, filter on `site`. The
   `strategy` field says what is needed: `PUBLIC` needs no browser;
   `COOKIE` / `INTERCEPT` / `UI` need the extension and a login.
3. Run one small, read-only command for that site that only returns real content
   when logged in (a feed, saved items, a search). Real rows → done.

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

Read `opencli-usage` before the first real task.
`${CLAUDE_PLUGIN_ROOT}/skills/setup-opencli/references/pitfalls.md` covers
failure modes those skills don't: upgrades deleting edited adapters, sessions
losing their tab, uploads, rate limits.

## Never

- install anything before the user's yes in §1
- `sudo npm install -g`
- type the user's passwords or solve CAPTCHAs for them
- keep hitting a site after a CAPTCHA or "too many requests" — stop and tell the
  user (`references/pitfalls.md` § Rate limits)
