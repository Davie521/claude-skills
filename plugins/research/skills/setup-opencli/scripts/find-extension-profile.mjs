#!/usr/bin/env node
// Which Chrome profile has the OpenCLI extension, is it enabled, and which
// profiles is Chrome using? Read-only; Node built-ins only.
//
//   node find-extension-profile.mjs [--user-data-dir <dir>] [--extension-id <id>]
//
// Finds the Web Store install by ID, and unpacked installs ("Load unpacked"
// from a release zip, which get a path-derived ID) by their manifest name.
//
// Prints one JSON object. `verdict` is one of:
//   ok                      enabled in a profile Chrome is using
//   wrong_profile_open      enabled somewhere, but not in the profile(s) in use
//   installed_but_disabled  installed, disabled in every profile
//   not_installed           no profile has it
//   chrome_not_found        no Chrome user-data dir (exit 2)
//   local_state_unreadable  user-data dir exists but `Local State` won't parse (exit 3)
// `multipleProfiles: true` means it is enabled in more than one profile; OpenCLI
// then needs a default (`opencli profile use <name>`).

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const STORE_EXTENSION_ID = 'ildkmabpimmkaediidaifkhjpohdnifk';
const EXTENSION_NAME = 'OpenCLI';
// Chrome's Manifest::Location values for unpacked / command-line loaded extensions.
const UNPACKED_LOCATIONS = new Set([4, 8]);
const USAGE = 'usage: find-extension-profile.mjs [--user-data-dir <dir>] [--extension-id <id>]';

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

function usageError(message) {
  console.error(`${message}\n${USAGE}`);
  process.exit(64);
}

function parseArgs(argv) {
  const opts = { userDataDir: defaultUserDataDir(), extensionId: STORE_EXTENSION_ID };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--help' || a === '-h') {
      console.log(USAGE);
      process.exit(0);
    } else if (a === '--user-data-dir' || a === '--extension-id') {
      const value = argv[++i];
      if (!value || value.startsWith('--')) usageError(`missing value for ${a}`);
      opts[a === '--user-data-dir' ? 'userDataDir' : 'extensionId'] = value;
    } else {
      usageError(`unknown argument: ${a}`);
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

// Per-extension settings, merging the older "Preferences" with the current
// "Secure Preferences" field by field (Secure wins on conflicts).
function extensionSettings(profileDir) {
  const merged = {};
  let found = false;
  for (const file of ['Preferences', 'Secure Preferences']) {
    const settings = readJson(path.join(profileDir, file))?.extensions?.settings;
    if (!settings || typeof settings !== 'object') continue;
    found = true;
    for (const [id, s] of Object.entries(settings)) {
      if (s && typeof s === 'object') merged[id] = { ...merged[id], ...s };
    }
  }
  return { settings: merged, found };
}

// true / false, or null when Chrome left no recognisable state field.
function enabledFrom(s) {
  if (Array.isArray(s.disable_reasons)) return s.disable_reasons.length === 0;
  if (typeof s.disable_reasons === 'number') return s.disable_reasons === 0;
  if (typeof s.state === 'number') return s.state === 1;
  return null;
}

function findInstalls(settings, extensionId) {
  const installs = [];
  for (const [id, s] of Object.entries(settings)) {
    let kind = null;
    if (id === extensionId) kind = 'store';
    else if (UNPACKED_LOCATIONS.has(s.location) && typeof s.path === 'string'
      && readJson(path.join(s.path, 'manifest.json'))?.name === EXTENSION_NAME) kind = 'unpacked';
    if (kind) installs.push({ id, kind, enabled: enabledFrom(s) });
  }
  return installs;
}

const { userDataDir, extensionId } = parseArgs(process.argv.slice(2));
const localStatePath = path.join(userDataDir, 'Local State');
if (!fs.existsSync(localStatePath)) {
  console.log(JSON.stringify({ verdict: 'chrome_not_found', userDataDir }, null, 2));
  process.exit(2);
}
const localState = readJson(localStatePath);
if (!localState || typeof localState !== 'object') {
  console.log(JSON.stringify({ verdict: 'local_state_unreadable', userDataDir }, null, 2));
  process.exit(3);
}

const profileState = localState.profile ?? {};
const profiles = Object.entries(profileState.info_cache ?? {}).map(([dir, info]) => {
  const { settings, found } = extensionSettings(path.join(userDataDir, dir));
  const installs = findInstalls(settings, extensionId);
  // Enabled if any install is enabled; null (unknown) is not evidence of disabled.
  let enabled = false;
  if (installs.some((x) => x.enabled === true)) enabled = true;
  else if (installs.some((x) => x.enabled === null)) enabled = null;
  return { dir, name: info?.name ?? null, preferencesFound: found, installs, enabled };
});

const lastUsed = typeof profileState.last_used === 'string' ? profileState.last_used : null;
const lastActive = Array.isArray(profileState.last_active_profiles) ? profileState.last_active_profiles : [];
// Profiles Chrome is (or was last) using; falls back to last_used when the list is empty.
const inUse = lastActive.length > 0 ? lastActive : lastUsed ? [lastUsed] : [];
const usable = profiles.filter((p) => p.installs.length > 0 && p.enabled !== false).map((p) => p.dir);

let verdict;
if (!profiles.some((p) => p.installs.length > 0)) verdict = 'not_installed';
else if (usable.length === 0) verdict = 'installed_but_disabled';
else if (inUse.length > 0 && !inUse.some((d) => usable.includes(d))) verdict = 'wrong_profile_open';
else verdict = 'ok';

console.log(JSON.stringify({
  verdict,
  openThisProfile: usable.find((d) => inUse.includes(d)) ?? usable[0] ?? null,
  multipleProfiles: usable.length > 1,
  inUse,
  lastUsed,
  profiles,
  userDataDir,
}, null, 2));
