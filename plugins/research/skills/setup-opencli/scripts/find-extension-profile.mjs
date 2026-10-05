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
//   ok                      enabled in a profile Chrome is using (or Chrome has
//                           no record of which profile is in use)
//   wrong_profile_open      enabled somewhere, but not in the profile(s) in use
//   installed_but_disabled  installed, disabled in every profile
//   not_installed           no profile has it
//   unknown                 not found, but some profile's preference files won't parse
//   chrome_not_found        no Chrome user-data dir (exit 2)
//   local_state_unreadable  user-data dir exists but `Local State` won't parse (exit 3)
// `multipleProfiles: true`: enabled in more than one profile — fine unless they
// are open at the same time, then OpenCLI wants `opencli profile use <name>`.
// `duplicateInProfile: true`: one profile has two enabled copies (e.g. Web Store
// plus Load unpacked); each connects separately.
// Exit 64 on bad arguments.

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
      return path.join(process.env.XDG_CONFIG_HOME || path.join(home, '.config'), 'google-chrome');
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

const asObject = (x) => (x && typeof x === 'object' && !Array.isArray(x) ? x : null);

// Extension settings from current Chrome's "Secure Preferences" and older
// builds' "Preferences". `readable` is false when neither file parses.
function extensionSettings(profileDir) {
  const secureFile = readJson(path.join(profileDir, 'Secure Preferences'));
  const prefsFile = readJson(path.join(profileDir, 'Preferences'));
  return {
    secure: asObject(secureFile?.extensions?.settings) ?? {},
    prefs: asObject(prefsFile?.extensions?.settings) ?? {},
    readable: secureFile !== null || prefsFile !== null,
  };
}

// true / false, or null when Chrome left no recognisable state field.
function enabledFrom(s) {
  if (Array.isArray(s.disable_reasons)) return s.disable_reasons.length === 0;
  if (typeof s.disable_reasons === 'number') return s.disable_reasons === 0;
  if (typeof s.state === 'number') return s.state === 1;
  return null;
}

function findInstalls({ secure, prefs }, extensionId) {
  const installs = [];
  for (const id of new Set([...Object.keys(secure), ...Object.keys(prefs)])) {
    const s = asObject(secure[id]);
    const p = asObject(prefs[id]);
    if (!s && !p) continue;
    const location = s?.location ?? p?.location;
    const extPath = s?.path ?? p?.path;
    let kind = null;
    if (id === extensionId) kind = 'store';
    else if (UNPACKED_LOCATIONS.has(location) && typeof extPath === 'string'
      && readJson(path.join(extPath, 'manifest.json'))?.name === EXTENSION_NAME) kind = 'unpacked';
    // Secure Preferences is authoritative; Preferences only fills in a missing state.
    if (kind) installs.push({ id, kind, enabled: (s ? enabledFrom(s) : null) ?? (p ? enabledFrom(p) : null) });
  }
  return installs;
}

// Profile directories: Local State's info_cache, or a directory scan when it is empty.
function profileDirs(userDataDir, infoCache) {
  const known = Object.entries(asObject(infoCache) ?? {});
  if (known.length > 0) return known.map(([dir, info]) => ({ dir, name: info?.name ?? null }));
  let entries = [];
  try {
    entries = fs.readdirSync(userDataDir, { withFileTypes: true });
  } catch {}
  return entries
    .filter((e) => e.isDirectory() && (e.name === 'Default' || /^Profile \d+$/.test(e.name)))
    .map((e) => ({ dir: e.name, name: null }));
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

const profileState = asObject(localState.profile) ?? {};
const profiles = profileDirs(userDataDir, profileState.info_cache).map(({ dir, name }) => {
  const settings = extensionSettings(path.join(userDataDir, dir));
  const installs = findInstalls(settings, extensionId);
  // Enabled if any install is enabled; null (unknown) is not evidence of disabled.
  let enabled = false;
  if (installs.some((x) => x.enabled === true)) enabled = true;
  else if (installs.some((x) => x.enabled === null)) enabled = null;
  return { dir, name, preferencesReadable: settings.readable, installs, enabled };
});

const lastUsed = typeof profileState.last_used === 'string' ? profileState.last_used : null;
const lastActive = Array.isArray(profileState.last_active_profiles) ? profileState.last_active_profiles : [];
// Profiles Chrome is (or was last) using; falls back to last_used when the list is empty.
const inUse = lastActive.length > 0 ? lastActive : lastUsed ? [lastUsed] : [];
const usable = profiles.filter((p) => p.installs.length > 0 && p.enabled !== false).map((p) => p.dir);

let verdict;
if (!profiles.some((p) => p.installs.length > 0)) {
  verdict = profiles.some((p) => !p.preferencesReadable) ? 'unknown' : 'not_installed';
}
else if (usable.length === 0) verdict = 'installed_but_disabled';
else if (inUse.length > 0 && !inUse.some((d) => usable.includes(d))) verdict = 'wrong_profile_open';
else verdict = 'ok';

console.log(JSON.stringify({
  verdict,
  openThisProfile: usable.find((d) => inUse.includes(d)) ?? usable[0] ?? null,
  multipleProfiles: usable.length > 1,
  duplicateInProfile: profiles.some((p) => p.installs.filter((x) => x.enabled !== false).length > 1),
  inUse,
  lastUsed,
  profiles,
  userDataDir,
}, null, 2));
