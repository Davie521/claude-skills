# OpenCLI pitfalls the bundled skills don't cover

Symptom → cause → fix. Collected from real use of opencli 1.8.x on macOS.

## Upgrades

**Symptom:** after `npm install -g @jackwener/opencli` (an upgrade), a site you
had customised behaves like stock again. No error, nothing in npm's output.

**Cause:** the postinstall script (`scripts/fetch-adapters.js`) deletes the whole
`~/.opencli/clis/<site>/` override for every site whose official adapter files
changed — whether or not you edited it. No backup, not moved to the trash. A
release can touch most sites' adapter files, so one plain upgrade can take nearly
all of your overrides at once.

**Fix:** if the upgrade was prompted by opencli's `Update available` notice
rather than asked for by the user, ask before doing anything. Then run
`opencli adapter status`. If it lists any local overrides:

```bash
cp -a ~/.opencli/clis ~/.opencli/clis.bak-$(date +%F-%H%M%S)
opencli daemon stop          # so the new version starts a fresh daemon
npm install -g @jackwener/opencli@<version> --ignore-scripts   # <version>: npm view @jackwener/opencli version
opencli doctor
```

Run these one at a time — never chain the backup and the install into one
command — and upgrade only after `/bin/ls ~/.opencli/` shows the backup directory.

Use `--ignore-scripts` on every upgrade while you have overrides: a skipped
postinstall also leaves `~/.opencli/adapter-manifest.json` at the old version, so
a later plain upgrade diffs against an even older baseline. What it costs:
shell completion isn't refreshed, and your overrides are never cleaned up
automatically — they keep shadowing upstream fixes for those sites. Drop one you
no longer need with `opencli adapter reset <site>`.

No local overrides → a plain upgrade is safe; if doctor then reports
`Stale daemon detected`, run `opencli daemon restart`.

## BROWSER_CONNECT right after a daemon restart

The extension has not reconnected yet (its back-off goes up to 15 s). Re-run
`opencli doctor` every ~10 s until it shows `[OK] Extension` — give up after
~30 s and go back to the SKILL.md §4 table — then retry the same command.

`opencli daemon status` is only a reliable check with one Chrome profile
connected: it ignores the saved default, so with two or more it always reports
`… connected, none selected`. If you do match its `Extension: connected` line,
match the whole string (`grep -q 'Extension: connected'`): a pattern like
`*connected*` also matches `disconnected`.

## `attach failed: Cannot access a chrome-extension:// URL of different extension`

Chrome refuses to attach its debugger when the target tab contains a frame
belonging to another extension. Two common causes:

1. **Another extension injects frames into the page** — password managers such
   as 1Password often do on login forms. OpenCLI's own `opencli-browser` skill
   says to disable such extensions temporarily. Ask the user before touching
   their extensions.
2. **On `opencli browser <session> …`, the session is pointed at the wrong tab**
   (e.g. an extension page). Re-target it:

   ```bash
   opencli browser <session> unbind
   opencli browser <session> open <url>   # opencli opens a tab it controls
   ```

   `opencli browser <session> bind` also works, but it attaches whatever tab is
   in front — possibly `about:blank` or a page the user is reading — and a bound
   tab refuses `tab new / select / close`.

On a site adapter (`opencli <site> …`) where neither applies, retry once; if it
persists, collect a trace and report it upstream
(`opencli skills read opencli-autofix`).

## `eval` suddenly returns nothing

`opencli browser <session> eval …` keeps succeeding but returns empty arrays /
zero elements. The session's tab drifted to `about:blank`. In batch work, check
`location.href` before and after; if it drifted, `unbind` + `open <url>`. Put a
multi-step form interaction into **one** `eval` instead of many commands — fewer
chances to lose the tab midway.

## `file://` URLs are refused

`opencli browser` only accepts http(s). To look at a local HTML file, serve its
directory: `python3 -m http.server <port> --bind 127.0.0.1` (on macOS `python3`
needs the Xcode Command Line Tools — without them it opens an install dialog),
open `http://127.0.0.1:<port>/<file>`, and stop the server afterwards.

## `upload` returns `{"code":-32000,"message":"Not allowed"}`

Per Chromium's source, file inputs can only be set when the extension has
**Allow access to file URLs**, which is off for store installs. (Not verified
end to end here.) Turning it on lets any local process that can reach the daemon
make Chrome read local files — switch it on only while uploading.

Workaround without the toggle, for small files: inside one `eval`, build
`new File([bytes], name, { type })`, put it in a `DataTransfer`, assign
`input.files = dt.files`, then dispatch bubbling `input` and `change` events.
Many upload widgets clear the input right away, so success means the page shows
the file name and size, not `input.files.length`.

## "AUTH_REQUIRED" but the user is sure they're logged in

Often both sides are half right: sites keep identity cookies (nickname, avatar)
after the session expires, so the browser looks logged in while it isn't. Judge
by a page that requires login (orders, bookmarks, shelf): a login button there
means logged out. Conversely, `Selector not found: X` is frequently just a
readiness-wait selector timing out, not proof the whole page was redesigned.

## Rate limits

Sites with anti-bot systems (Xiaohongshu, Twitter/X, Weibo, Boss Zhipin,
Taobao, …) flag bursts from one logged-in account. Space requests by seconds,
keep batches small, and at the first CAPTCHA, "too many requests" / 操作频繁, or
forced re-login: **stop** and tell the user. Never retry in a loop — the account
at risk is theirs.
