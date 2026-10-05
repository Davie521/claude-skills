#!/usr/bin/env node
// Which Chrome profile has the OpenCLI extension, is it enabled, and which
// profiles did Chrome last have open? Read-only; Node built-ins only.
//
//   node find-extension-profile.mjs [--user-data-dir <dir>] [--extension-id <id>]
//
// Prints one JSON object. `verdict` is one of:
//   ok                     extension enabled in a profile Chrome last had open
//   wrong_profile_open     enabled somewhere, but not in the profiles last open
//   installed_but_disabled present on disk, disabled in every profile
//   not_installed          no profile has it
// Exit 2 when no Chrome user-data dir is found.

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const OPENCLI_EXTENSION_ID = 'ildkmabpimmkaediidaifkhjpohdnifk';

function defaultUserDataDir() {
  const home = os.homedir();
  switch (process.platform) {
    case 'darwin':
      return path.join(home, 'Library', 'Application Support', 'Google', 'Chrome');
    case 'win32':
      return path.join(process.env.LOCALAPPDATA ?? path.join(home, 'AppData', 'Local'), 'Google', 'Chrome', 'User Data');
    default:
      return path.join(home, '.config', 'google-chrome');
  }
}

function parseArgs(argv) {
  const opts = { userDataDir: defaultUserDataDir(), extensionId: OPENCLI_EXTENSION_ID };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') {
      console.log('usage: find-extension-profile.mjs [--user-data-dir <dir>] [--extension-id <id>]');
      process.exit(0);
    } else if (a === '--user-data-dir') opts.userDataDir = argv[++i];
    else if (a === '--extension-id') opts.extensionId = argv[++i];
    else {
      console.error(`unknown argument: ${a}`);
      process.exit(64);
    }
  }
  return opts;
}

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

// true / false, or null when Chrome left no recognisable setting for it.
function extensionEnabled(profileDir, id) {
  // Current Chrome keeps extension settings in "Secure Preferences"; older builds in "Preferences".
  for (const file of ['Secure Preferences', 'Preferences']) {
    const s = readJson(path.join(profileDir, file))?.extensions?.settings?.[id];
    if (!s) continue;
    if (Array.isArray(s.disable_reasons)) return s.disable_reasons.length === 0;
    if (typeof s.disable_reasons === 'number') return s.disable_reasons === 0;
    if (typeof s.state === 'number') return s.state === 1;
    return null;
  }
  return null;
}

const { userDataDir, extensionId } = parseArgs(process.argv.slice(2));
const localState = readJson(path.join(userDataDir, 'Local State'));
if (!localState) {
  console.log(JSON.stringify({ verdict: 'chrome_not_found', userDataDir }, null, 2));
  process.exit(2);
}

const profileState = localState.profile ?? {};
const profiles = Object.entries(profileState.info_cache ?? {}).map(([dir, info]) => {
  const profileDir = path.join(userDataDir, dir);
  const installed = fs.existsSync(path.join(profileDir, 'Extensions', extensionId));
  return { dir, name: info?.name ?? null, installed, enabled: installed ? extensionEnabled(profileDir, extensionId) : false };
});

// enabled === null means "unknown", which is not evidence of disabled.
const usable = profiles.filter((p) => p.installed && p.enabled !== false).map((p) => p.dir);
const lastActive = profileState.last_active_profiles ?? [];

let verdict;
if (!profiles.some((p) => p.installed)) verdict = 'not_installed';
else if (usable.length === 0) verdict = 'installed_but_disabled';
else if (lastActive.length > 0 && !lastActive.some((d) => usable.includes(d))) verdict = 'wrong_profile_open';
else verdict = 'ok';

console.log(JSON.stringify({
  verdict,
  openThisProfile: usable[0] ?? null,
  lastUsed: profileState.last_used ?? null,
  lastActive,
  profiles,
  userDataDir,
  extensionId,
}, null, 2));
