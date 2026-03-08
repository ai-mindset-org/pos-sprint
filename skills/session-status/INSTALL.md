# Session Status — Installation & Reference

## Concept

A compact terminal statusbar for Claude Code that shows at a glance:

1. **Model** — which Claude model is active (O / S / H)
2. **Context fill** — how full the context window is, as 5 blocks (■■□□□)
3. **Rate-limit utilization** — 5-hour and 7-day API usage pulled from live Anthropic response headers
4. **Git status** — current branch + dirty/untracked state

The context fill adds a fixed **+17%** to `used_percentage` (from Claude Code's JSON) to correct for a
hidden autocompact buffer that is never reflected in the JSON.

**Why +17%:** Claude Code permanently reserves ~33k tokens (~16.5% of a 200k context window) as
headroom for the autocompact summarization workflow. This reservation is always present but excluded
from `used_percentage`, which counts only `input_tokens + cache_creation_tokens + cache_read_tokens`.
The result is that the raw JSON number systematically understates how full the context actually is:
when `used_percentage` reads 78%, the window is effectively 78% + 16.5% ≈ **95% full**, and
autocompact is about to fire. Adding +17% in the script corrects this so the bar reflects the
true fill level rather than the artificially low JSON value.

Rate-limit data requires **patching Claude Code's HTTP transport** via `NODE_OPTIONS=--require`, so the
interceptor can read Anthropic's rate-limit headers from each API response without making extra requests.

---

## Platform

**Windows only. Requires Claude Code installed via npm (not the native `.exe` installer).**

Claude Code ships multiple binaries:

| Binary | Runtime | NODE_OPTIONS --require |
|--------|---------|----------------------|
| `~/.local/bin/claude.exe` | **Bun** (native installer) | ✗ Ignored — Bun ignores Node.js env vars |
| `npm\claude.cmd` → `node cli.js` | **Node.js v24+** | ✓ Works, but NODE_OPTIONS not pre-set |
| `npm\claude.ps1` → `node cli.js` | **Node.js v24+** | ✓ Works, but NODE_OPTIONS not pre-set |

`claude.exe` (Bun) comes first in PATH, so it wins over the npm wrappers without intervention.
A PowerShell `function claude` overrides all PATH resolution (functions beat executables in PS) and calls
`node cli.js` directly with NODE_OPTIONS pre-injected — bypassing both Bun and the npm wrappers.

---

## Dependencies

| Tool | Purpose |
|------|---------|
| `jq` | JSON parsing in statusline.sh (`winget install jqlang.jq`) |
| `~/.claude/statusline.sh` | Statusline script |
| `~/.claude/rate-limit-cache.json` | Rate-limit % cache (written by interceptor hook) |
| `~/.claude/hooks/rate-limit-interceptor.js` | Patches `node:https` + `globalThis.fetch` + undici to capture Anthropic response headers |

---

## Fresh Install — New System Setup

### Step 1 — Install prerequisites

**Node.js v24+** (required — the native `claude.exe` uses Bun which ignores `NODE_OPTIONS`):
```powershell
winget install OpenJS.NodeJS.LTS
```

**jq** (required — statusline.sh uses it to parse JSON):
```powershell
winget install jqlang.jq
```

> **Note:** winget installs jq into `%LOCALAPPDATA%\Microsoft\WinGet\Packages\jqlang.jq_...\` and adds
> it to the Windows User PATH. PowerShell and cmd.exe pick it up automatically after a terminal restart.
> Git Bash does **not** inherit Windows User PATH changes — add it manually to `~/.bashrc`:
> ```bash
> export PATH="/c/Users/<YOU>/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_Microsoft.Winget.Source_8wekyb3d8bbwe:$PATH"
> ```

Restart your terminal after installing. Verify:
```powershell
node --version   # v24.x.x
jq --version     # jq-1.x.x
```

### Step 2 — Claude Code settings.json (statusLine command)

Add the `statusLine` block to `~/.claude/settings.json` (create the file if it does not exist):

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash --login -c 'bash ~/.claude/statusline.sh'"
  }
}
```

> **Why `--login`?** Claude Code spawns `bash` in non-interactive, non-login mode — so `~/.bashrc` is
> never sourced and `jq` (installed via winget) is not on the PATH. `--login` forces bash to source
> `~/.bash_profile` → `~/.bashrc` where the jq PATH export lives, making `jq` available to
> `statusline.sh` at runtime.

### Step 3 — Install npm package

```powershell
npm install -g @anthropic-ai/claude-code
```

Installs `cli.js` at `%APPDATA%\npm\node_modules\@anthropic-ai\claude-code\cli.js`.

### Step 4 — Copy files

```
~/.claude/
  hooks/rate-limit-interceptor.js   ← copy from _skills/skills/session-status/
  statusline.sh                     ← copy from _skills/skills/session-status/
  skills/session-status/SKILL.md    ← sync from _skills/skills/session-status/SKILL.md
```

### Step 5 — NODE_OPTIONS (Windows User env var, survives reboots)

```powershell
[System.Environment]::SetEnvironmentVariable(
  'NODE_OPTIONS',
  '--require C:\Users\<YOU>\.claude\hooks\rate-limit-interceptor.js',
  'User'
)
```

### Step 6 — PowerShell profile

Defines `function claude` that bypasses **both** `claude.exe` (Bun, first in PATH) and the npm
wrappers (`claude.ps1` / `claude.cmd`), calling `node cli.js` directly with NODE_OPTIONS pre-set.
PS functions have higher precedence than any PATH-resolved binary.

> **Execution Policy — required before this step works.** PowerShell will silently skip `.ps1`
> profile files when the policy is `Restricted` (the default on fresh/corporate machines). Run this
> once before editing your profile:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Verify with `Get-ExecutionPolicy` — it must show `RemoteSigned` (or `Unrestricted`).

```powershell
# $PROFILE = C:\Users\<YOU>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
function claude {
    $interceptor = "C:\Users\<YOU>\.claude\hooks\rate-limit-interceptor.js"
    $cliJs = "C:\Users\<YOU>\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js"
    if ($env:NODE_OPTIONS -notlike "*rate-limit-interceptor*") {
        $env:NODE_OPTIONS = "--require $interceptor $env:NODE_OPTIONS".Trim()
    }
    node $cliJs @args
}
```

Create profile if missing:
```powershell
New-Item -ItemType Directory -Force -Path (Split-Path $PROFILE)
New-Item -ItemType File -Force -Path $PROFILE
```

### Step 7a — Git Bash wrapper (~/.bashrc function)

Git Bash uses a shell **function** in `~/.bashrc` — functions beat PATH-resolved binaries, so this
overrides `claude.exe` (Bun) without needing PATH changes.

Add to `~/.bashrc`:
```bash
# Claude Code wrapper: routes `claude` through node+cli.js so that
# NODE_OPTIONS --require (rate-limit interceptor) actually takes effect.
# The bundled claude.exe ignores --require; node+cli.js respects it.
claude() {
  local INTERCEPTOR="C:\\Users\\<YOU>\\.claude\\hooks\\rate-limit-interceptor.js"
  local CLI_JS="C:/Users/<YOU>/AppData/Roaming/npm/node_modules/@anthropic-ai/claude-code/cli.js"
  if [[ "${NODE_OPTIONS}" != *"rate-limit-interceptor"* ]]; then
    export NODE_OPTIONS="--require ${INTERCEPTOR} ${NODE_OPTIONS}"
  fi
  node "${CLI_JS}" "$@"
}
```

Verify: `type claude` → must show `claude is a function`, not a file path.

Note: `~/bin/claude` (a file wrapper) is shadowed by the function in interactive shells.
It can serve as a fallback for non-interactive scripts that source neither `.bashrc` nor `.bash_profile`.

### Step 7b — cmd.exe wrapper (~\bin\claude.cmd + Windows PATH)

cmd.exe has no shell-function mechanism. The wrapper must be a `.cmd` file that wins over
`claude.exe` (Bun) in PATH. Two requirements:
1. `C:\Users\<YOU>\bin\claude.cmd` exists
2. `C:\Users\<YOU>\bin` is in Windows User PATH **before** `.local\bin`

**Add `C:\Users\<YOU>\bin` to Windows User PATH** (required — without this, cmd.exe finds `claude.exe` first):

```powershell
# Run in PowerShell
$current = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
if ($current -notlike "*Users\<YOU>\bin*") {
    [System.Environment]::SetEnvironmentVariable(
        'PATH',
        "C:\Users\<YOU>\bin;$current",
        'User'
    )
}
```

**`~\bin\claude.cmd`** — create this file:
```bat
@ECHO off
SET INTERCEPTOR=C:\Users\<YOU>\.claude\hooks\rate-limit-interceptor.js
SET CLI_JS=C:\Users\<YOU>\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js

echo %NODE_OPTIONS% | findstr /C:"rate-limit-interceptor" >nul 2>&1
IF ERRORLEVEL 1 SET NODE_OPTIONS=--require %INTERCEPTOR% %NODE_OPTIONS%

node "%CLI_JS%" %*
```

Verify in a **new** cmd.exe (not spawned from Git Bash):
```bat
where claude
:: Must return C:\Users\<YOU>\bin\claude.cmd first, NOT claude.exe from .local\bin
```

> Note: the npm `claude.cmd` at `%APPDATA%\npm\claude.cmd` calls `node cli.js` but does NOT inject
> NODE_OPTIONS. It would work IF `NODE_OPTIONS` is set globally (Step 3) AND it wins over `claude.exe`.
> But `claude.exe` (.EXE) beats `claude.cmd` when both are in the same dir, and `.local\bin` (with
> `claude.exe`) typically precedes `%APPDATA%\npm` in User PATH. Hence the dedicated wrapper in `~\bin\`.

### Step 8 — Verify

**PowerShell** (open a new terminal):
```powershell
Get-Command claude | Select-Object CommandType  # Must be: Function
claude --version                                # Should print version
# Make one API call, then:
cat ~/.claude/interceptor-debug.log             # Must contain "interceptor loaded — pid=..."
cat ~/.claude/rate-limit-cache.json             # Must contain five_hour_pct, seven_day_pct
```

**Git Bash** (open a new terminal):
```bash
type claude       # Must show: claude is a function
claude --version  # Should print version
```

**cmd.exe** (open a new cmd.exe from Start Menu — NOT from Git Bash):
```bat
where claude
:: First result must be C:\Users\<YOU>\bin\claude.cmd, NOT .local\bin\claude.exe
```

### Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Log empty after restart | PS profile not loading | Check `$PROFILE` path, run `. $PROFILE` |
| Cache stale (yesterday) | Bun binary still used | Verify `Get-Command claude` shows Function, not Application |
| `node: command not found` | Node not in PATH | Install Node.js, restart terminal |
| `cli.js` not found | npm package not installed | `npm install -g @anthropic-ai/claude-code` |
| cmd.exe uses claude.exe (Bun) | `~\bin` not in Windows PATH | Add `C:\Users\<YOU>\bin` to User PATH before `.local\bin` (Step 7b) |
| Git Bash uses file, not function | `.bashrc` not sourced | Check `~/.bash_profile` sources `~/.bashrc`; run `. ~/.bashrc` |
| Statusline shows only `S ■□□□□` (no rate data) | `jq` not installed | `winget install jqlang.jq`, restart terminal |
| Statusline blank / jq not found in statusLine | `bash` not launched as login shell | Ensure settings.json uses `"bash --login -c 'bash ~/.claude/statusline.sh'"` (Step 2) |
| PS profile silently not loading | Execution Policy = Restricted | See below |
| Function defined in wrong profile | PS 5.1 vs PS 7+ different paths | See below |

#### If the PowerShell function never loads

**Cause A — Execution Policy (most common on corporate/fresh machines)**

PowerShell refuses to run `.ps1` files when policy is `Restricted`. The profile exists, the function is written — but PowerShell silently skips it. `claude.exe` (Bun) wins every time.

```powershell
# Diagnose
Get-ExecutionPolicy          # If "Restricted" — this is the cause
Get-Command claude | Select-Object CommandType  # Will show "Application", not "Function"

# Fix (current user only, no admin required)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Reload profile
. $PROFILE

# Verify
Get-Command claude | Select-Object CommandType  # Must show "Function"
```

**Cause B — Wrong profile path (PS 5.1 vs PS 7+)**

Windows ships with PowerShell 5.1 (`powershell.exe`) and PowerShell 7+ (`pwsh.exe`). They use **different profile files**:

| Shell | Profile path |
|-------|-------------|
| PS 5.1 (`powershell.exe`) | `...\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` |
| PS 7+ (`pwsh.exe`) | `...\PowerShell\Microsoft.PowerShell_profile.ps1` |

If you wrote the function into the PS 5.1 profile but launch `pwsh`, it will never load. Check which shell you're in and which `$PROFILE` it resolves to:

```powershell
$PSVersionTable.PSVersion   # Check version
$PROFILE                    # Check which file this shell uses
```

Write the `function claude { ... }` block into whichever file `$PROFILE` points to in your actual shell.

#### If Git Bash function never loads

Git Bash login shells read `~/.bash_profile`, **not** `~/.bashrc`. The `claude` function defined in `~/.bashrc` never loads unless `~/.bash_profile` explicitly sources it.

```bash
# Diagnose
type claude   # If path to file (not "is a function") — .bashrc not sourced

# Fix: ensure ~/.bash_profile contains:
[[ -f ~/.bashrc ]] && source ~/.bashrc

# Reload
source ~/.bash_profile

# Verify
type claude   # Must show: claude is a function
```

---

## Format & Legend

```
S ■□□□□ ▁◕ħ ▁○ẁ ▁○ś master+
│ │      │││  │││  │││ │
│ │      │││  │││  │││ └─ git branch (* = changes, + = untracked)
│ │      │││  │││  ││└─── ś = 7-day Sonnet limit label
│ │      │││  │││  │└──── cycle position ○◔◑◕● (○=just reset → ●=about to reset)
│ │      │││  │││  └───── vertical bar = usage level ▁▂▃▄▅▆▇█
│ │      │││  ││└──────── ẁ = 7-day all-models limit label
│ │      │││  │└───────── cycle position
│ │      │││  └────────── vertical bar = usage level
│ │      ││└────────────── ħ = 5-hour limit label
│ │      │└─────────────── cycle position
│ │      └──────────────── vertical bar = usage level
│ └─────────────────────── ctx: 5 blocks ■=filled □=free, ceil((ctx_used+17)/20)
└───────────────────────── model: O / S / H
```

`~` prefix on usage = cache stale (>60 min since last API call updated it).

**Color:** monochrome `\033[38;5;102m` (grey-blue) across all elements.

---

## Rate-limit cache (~/.claude/rate-limit-cache.json)

Written automatically by the interceptor hook on each Anthropic API call.

**Manual reseed** (when cache is stale/missing):
```json
{
  "five_hour_pct": <value>,
  "seven_day_pct": <all_models_value>,
  "seven_day_sonnet_pct": <sonnet_value>,
  "_cached_at": <Date.now()>
}
```

---

## ~/.claude/statusline.sh

```bash
#!/usr/bin/env bash
# statusline.sh — Claude Code terminal statusbar
# Dependencies: jq (winget install jqlang.jq)
# Input: JSON from Claude Code on stdin (e.g. '{"model":...,"context_window":...}')
input=$(cat)

# --- Model: O/S/H ---
_display=$(echo "$input" | jq -r '.model.display_name // ""' 2>/dev/null)
case "$_display" in
    *[Hh]aiku*)  model="H" ;;
    *[Oo]pus*)   model="O" ;;
    *[Ss]onnet*) model="S" ;;
    *)           model="S" ;;
esac
unset _display

# --- Working dir ---
cwd=$(echo "$input" | jq -r '.workspace.current_dir // ""' 2>/dev/null)
[ -z "$cwd" ] && cwd=$(pwd)

# --- Context fill ---
ctx_used=$(echo "$input" \
  | jq -r '.context_window.used_percentage // 0 | floor' 2>/dev/null)
[[ "$ctx_used" =~ ^[0-9]+$ ]] || ctx_used=0
# Add 17% constant for autocompact buffer (not exposed in JSON)
ctx_fill=$(( ctx_used + 17 ))
[ "$ctx_fill" -gt 100 ] && ctx_fill=100
# 5 blocks: filled count = ceil(ctx_fill / 20), capped at 5
filled=$(( (ctx_fill + 19) / 20 ))
[ "$filled" -gt 5 ] && filled=5
ctx=""
for i in 1 2 3 4 5; do
    if [ "$i" -le "$filled" ]; then ctx="${ctx}■"
    else                            ctx="${ctx}□"
    fi
done

# --- Git status (compact) ---
git_info=""
if git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
    branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null \
      | cut -c1-12)
    s=""
    git -C "$cwd" --no-optional-locks diff --quiet 2>/dev/null && \
    git -C "$cwd" --no-optional-locks diff --cached --quiet 2>/dev/null || s="*"
    [ -n "$(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard \
      2>/dev/null)" ] && s="${s}+"
    [ -n "$branch" ] && git_info=" ${branch}${s}"
fi

# --- Rate limit usage ---
usage_info=""
rl_cache="$HOME/.claude/rate-limit-cache.json"
if [ -f "$rl_cache" ]; then
    five_h=$(jq -r '.five_hour_pct  // empty' "$rl_cache" 2>/dev/null)
    seven_d=$(jq -r '.seven_day_pct // empty' "$rl_cache" 2>/dev/null)
    seven_s=$(jq -r '.seven_day_sonnet_pct // empty' "$rl_cache" 2>/dev/null)
    five_h_resets=$(jq -r '.five_hour_resets_at // empty' "$rl_cache" 2>/dev/null)
    seven_d_resets=$(jq -r '.seven_day_resets_at // empty' "$rl_cache" 2>/dev/null)
    seven_s_resets=$(jq -r '.seven_day_sonnet_resets_at // empty' "$rl_cache" 2>/dev/null)
    cached_at=$(jq -r '._cached_at // 0' "$rl_cache" 2>/dev/null)

    stale=""
    if [[ "$cached_at" =~ ^[0-9]+$ ]]; then
        age_min=$(( ( $(date +%s) * 1000 - cached_at ) / 60000 ))
        [ "$age_min" -gt 60 ] && stale="~"
    fi

    # Cycle indicator: ○=just reset → ●=about to reset (5 gradations)
    _CYCLE=(○ ◔ ◑ ◕ ●)
    cycle_char() {
        local ts=$1 window=$2
        [[ "$ts" =~ ^[0-9]+$ ]] || return
        local now remaining elapsed idx
        now=$(date +%s)
        remaining=$(( ts - now )); [ "$remaining" -lt 0 ] && remaining=0
        elapsed=$(( window - remaining )); [ "$elapsed" -lt 0 ] && elapsed=0
        idx=$(( elapsed * 5 / window )); [ "$idx" -gt 4 ] && idx=4
        echo "${_CYCLE[$idx]}"
    }

    # Vertical bar: 0-100% → ▁▂▃▄▅▆▇█
    _BARS=(▁ ▂ ▃ ▄ ▅ ▆ ▇ █)
    bar_char() {
        local p=$1 idx
        idx=$(( p * 8 / 100 )); [ "$idx" -gt 7 ] && idx=7
        echo "${_BARS[$idx]}"
    }

    parts=""
    [ -n "$five_h" ] && {
        r5=""; [[ "$five_h_resets" =~ ^[0-9]+$ ]] && r5="$(cycle_char "$five_h_resets" 18000)"
        parts="${parts}${stale}$(bar_char "$five_h")${r5}ħ"
    }
    [ -n "$seven_d" ] && {
        r7=""; [[ "$seven_d_resets" =~ ^[0-9]+$ ]] && r7="$(cycle_char "$seven_d_resets" 604800)"
        parts="${parts} $(bar_char "$seven_d")${r7}ẁ"
    }
    [ -n "$seven_s" ] && {
        rs=""; [[ "$seven_s_resets" =~ ^[0-9]+$ ]] && rs="$(cycle_char "$seven_s_resets" 604800)"
        parts="${parts} $(bar_char "$seven_s")${rs}ś"
    }
    [ -n "$parts" ] && usage_info="${parts# }"
fi

# --- Output ---
C=$'\033[38;5;102m' X=$'\033[0m'
printf '%s %s %s%s\n' "${C}${model}${X}" "${C}${ctx}${X}" "${C}${usage_info}${X}" "${C}${git_info}${X}"
```

---

## ~/.claude/hooks/rate-limit-interceptor.js

Patches `node:https`, `globalThis.fetch`, and `undici` (via `node:diagnostics_channel`) to capture
Anthropic rate-limit response headers. Activated via `NODE_OPTIONS=--require ...` (User env var).

API returns utilization as decimal (0.0–1.0). Interceptor multiplies by 100 before caching.

```js
/**
 * Claude Code Rate Limit Interceptor
 *
 * Captures Anthropic rate-limit utilization headers from existing API responses
 * (zero additional network requests).
 *
 * Writes ~/.claude/rate-limit-cache.json after each Anthropic API call:
 *   {
 *     "five_hour_pct": 10,
 *     "seven_day_pct": 10,
 *     "seven_day_sonnet_pct": 13,
 *     "five_hour_resets_at": "2026-03-07T14:00:00Z",
 *     "seven_day_resets_at": "2026-03-14T10:00:00Z",
 *     "_cached_at": 1741341600000
 *   }
 *
 * ── SETUP ────────────────────────────────────────────────────────────────────
 *
 * Windows (User env var — survives reboots, applies to all shells):
 *   PowerShell:
 *     [System.Environment]::SetEnvironmentVariable(
 *       'NODE_OPTIONS',
 *       '--require C:\Users\<YOU>\.claude\hooks\rate-limit-interceptor.js',
 *       'User'
 *     )
 *
 * Windows (claude.cmd only — safer, no effect on other Node processes):
 *   Edit C:\Users\<YOU>\AppData\Roaming\npm\claude.cmd
 *   Add before the last line:  SET NODE_OPTIONS=--require C:\Users\<YOU>\.claude\hooks\rate-limit-interceptor.js
 *
 * Linux / macOS (~/.bashrc or ~/.zshrc):
 *   export NODE_OPTIONS="--require $HOME/.claude/hooks/rate-limit-interceptor.js"
 *
 * macOS (launchd, for GUI apps that don't source .bashrc):
 *   launchctl setenv NODE_OPTIONS "--require $HOME/.claude/hooks/rate-limit-interceptor.js"
 *
 * ── WHY IT WORKS ─────────────────────────────────────────────────────────────
 *
 * cli.js uses `node:https` via property access (`VX1.request(...)`) and imported
 * reference (`import { request as DM5 }`). Both bind to the same module object
 * because require('https') === require('node:https'). Since --require runs before
 * cli.js parses, DM5 captures the patched function at import time.
 *
 * Headers captured (from each Anthropic API response):
 *   anthropic-ratelimit-unified-5h-utilization        → five_hour_pct
 *   anthropic-ratelimit-unified-7d-utilization        → seven_day_pct (all models)
 *   anthropic-ratelimit-unified-sonnet-utilization    → seven_day_sonnet_pct
 *   anthropic-ratelimit-unified-7d_sonnet-utilization → seven_day_sonnet_pct
 *   anthropic-ratelimit-unified-5h-reset              → five_hour_resets_at
 *   anthropic-ratelimit-unified-7d-reset              → seven_day_resets_at
 *   anthropic-ratelimit-unified-7d_sonnet-reset       → seven_day_sonnet_resets_at
 *   anthropic-ratelimit-unified-overage-utilization   → overage_pct
 *   anthropic-ratelimit-unified-overage-reset         → overage_resets_at
 *   anthropic-ratelimit-unified-representative-claim  → representative_claim
 *   anthropic-ratelimit-unified-fallback-percentage   → fallback_pct
 *   anthropic-ratelimit-unified-reset                 → resets_at
 */

'use strict';

const https = require('https');
const fs    = require('fs');
const os    = require('os');
const path  = require('path');

const CACHE_FILE = path.join(os.homedir(), '.claude', 'rate-limit-cache.json');
const DEBUG_LOG  = path.join(os.homedir(), '.claude', 'interceptor-debug.log');

// Rotate debug log at startup: keep at most MAX_LOG_BYTES of previous content.
const MAX_LOG_BYTES = 256 * 1024; // 256 KB
(function rotateLog() {
  try {
    const stat = fs.statSync(DEBUG_LOG);
    if (stat.size > MAX_LOG_BYTES) {
      // Keep the last MAX_LOG_BYTES/2 bytes so the file doesn't yo-yo
      const keep = MAX_LOG_BYTES / 2;
      const fd = fs.openSync(DEBUG_LOG, 'r');
      const buf = Buffer.alloc(keep);
      fs.readSync(fd, buf, 0, keep, stat.size - keep);
      fs.closeSync(fd);
      // Find first newline so we don't start mid-line
      const nl = buf.indexOf('\n');
      const trimmed = nl >= 0 ? buf.slice(nl + 1) : buf;
      fs.writeFileSync(DEBUG_LOG, trimmed);
    }
  } catch {
    // Non-fatal: log file may not exist yet, or no permission
  }
})();

function dbg(msg) {
  try { fs.appendFileSync(DEBUG_LOG, `[${new Date().toISOString()}] ${msg}\n`); } catch {}
}

// Header name → cache key mapping.
// Keys in PCT_DECIMAL_KEYS come from headers that return decimal 0.0–1.0 (multiply * 100).
// All other keys are stored verbatim.
const HEADER_MAP = {
  'anthropic-ratelimit-unified-5h-utilization':        'five_hour_pct',
  'anthropic-ratelimit-unified-7d-utilization':        'seven_day_pct',
  'anthropic-ratelimit-unified-sonnet-utilization':    'seven_day_sonnet_pct',
  'anthropic-ratelimit-unified-7d_sonnet-utilization': 'seven_day_sonnet_pct',
  'anthropic-ratelimit-unified-5h-reset':              'five_hour_resets_at',
  'anthropic-ratelimit-unified-7d-reset':              'seven_day_resets_at',
  'anthropic-ratelimit-unified-7d_sonnet-reset':       'seven_day_sonnet_resets_at',
  'anthropic-ratelimit-unified-overage-utilization':   'overage_pct',
  'anthropic-ratelimit-unified-overage-reset':         'overage_resets_at',
  'anthropic-ratelimit-unified-representative-claim':  'representative_claim',
  'anthropic-ratelimit-unified-fallback-percentage':   'fallback_pct',
  'anthropic-ratelimit-unified-reset':                 'resets_at',
};

// Keys whose header value is a decimal 0.0–1.0 (multiply by 100 to get percentage).
// All *-utilization and fallback-percentage headers return decimals per live observation.
const PCT_DECIMAL_KEYS = new Set([
  'five_hour_pct',
  'seven_day_pct',
  'seven_day_sonnet_pct',
  'overage_pct',
  'fallback_pct',
]);

/**
 * Convert a header value to its cache value.
 * Utilization headers (0.0–1.0) → rounded percentage (e.g. 0.123 → 12.3).
 * Returns null for unparseable utilization values instead of NaN/null confusion.
 */
function headerToValue(key, rawVal) {
  if (PCT_DECIMAL_KEYS.has(key)) {
    const pct = Math.round(Number(rawVal) * 100 * 10) / 10;
    return Number.isNaN(pct) ? null : pct;
  }
  return rawVal;
}

// ── In-memory write queue ────────────────────────────────────────────────────
// Prevents cache corruption from concurrent read-modify-write cycles.
// Node.js is single-threaded but multiple dc callbacks can fire across ticks;
// using an in-memory accumulator + synchronous flush avoids the TOCTOU gap.

let _memCache = null; // null = not loaded yet
let _writePending = false;

function loadCache() {
  if (_memCache !== null) return;
  try {
    _memCache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
  } catch {
    _memCache = {};
  }
}

function flushCache() {
  if (_writePending) return; // already scheduled
  _writePending = true;
  // Defer to next microtask so multiple same-tick updates are batched.
  Promise.resolve().then(() => {
    _writePending = false;
    try {
      fs.writeFileSync(CACHE_FILE, JSON.stringify(_memCache, null, 2));
    } catch (e) {
      dbg(`cache write error: ${e.message}`);
    }
  });
}

/**
 * Apply a header update object to the in-memory cache and schedule a flush.
 * @param {Object} update - { cacheKey: value, ... }
 */
function applyUpdate(update) {
  if (Object.keys(update).length === 0) return;
  loadCache();
  Object.assign(_memCache, update, { _cached_at: Date.now() });
  dbg(`rate-limit update: ${JSON.stringify(update)}`);
  flushCache();
}

// ── Helper: extract hostname ─────────────────────────────────────────────────

function extractHost(options) {
  if (!options) return '';
  if (typeof options === 'string') {
    try { return new URL(options).hostname; } catch { return ''; }
  }
  if (options instanceof URL) return options.hostname;
  return options.hostname || (options.host || '').split(':')[0];
}

// ── Layer 1: https.request patch ─────────────────────────────────────────────
// Fallback layer. Claude Code does NOT use this path currently (uses undici).
// Kept for forward-compatibility.

const _originalHttpsRequest = https.request.bind(https);

https.request = function claudeRateLimitInterceptor(options, callback) {
  const host = extractHost(options);
  dbg(`https.request → host=${host}`);

  if (!host.includes('anthropic.com')) {
    return _originalHttpsRequest(options, callback);
  }

  const wrapped = function(res) {
    dbg(`https response status=${res.statusCode}`);
    const update = {};
    for (const [header, key] of Object.entries(HEADER_MAP)) {
      const val = res.headers[header];
      if (val !== undefined) {
        const v = headerToValue(key, val);
        if (v !== null) update[key] = v;
      }
    }
    applyUpdate(update);
    if (callback) callback(res);
  };

  return _originalHttpsRequest(options, wrapped);
};

// NOTE: https.get is intentionally NOT patched separately.
// Node.js https.get calls https.request internally, so patching https.request
// is sufficient. Patching https.get separately would cause double-wrapping
// (the response callback would fire twice per https.get call).

dbg(`interceptor loaded — pid=${process.pid} node=${process.version}`);

// ── Layer 2: globalThis.fetch patch ─────────────────────────────────────────
// Fallback layer for fetch-based transports.

if (typeof globalThis.fetch === 'function') {
  const _originalFetch = globalThis.fetch;

  globalThis.fetch = async function claudeRateLimitFetchInterceptor(input, init) {
    let host = '';
    let fullUrl = '';
    try {
      fullUrl = typeof input === 'string' ? input
              : (input instanceof URL      ? input.href
              : (input && typeof input.url === 'string' ? input.url
              : (input && typeof input.toString === 'function' ? input.toString() : '')));
      host = new URL(fullUrl).hostname;
    } catch {}
    dbg(`fetch → host=${host}`);

    const response = await _originalFetch.call(this, input, init);

    if (host.includes('anthropic.com')) {
      dbg(`fetch response status=${response.status}`);
      const update = {};
      for (const [header, key] of Object.entries(HEADER_MAP)) {
        const val = response.headers.get(header);
        if (val !== null) {
          const v = headerToValue(key, val);
          if (v !== null) update[key] = v;
        }
      }
      applyUpdate(update);
    }

    return response;
  };
}

// ── Layer 3: diagnostics_channel (undici) ────────────────────────────────────
// PRIMARY working layer. Claude Code uses undici as its HTTP transport.
// https.request and globalThis.fetch patches do NOT intercept undici requests.

try {
  const dc = require('node:diagnostics_channel');

  dc.subscribe('undici:request:headers', function(msg) {
    const origin = String(msg.request && msg.request.origin || '');
    if (!origin.includes('anthropic.com')) return;

    const reqPath   = String(msg.request && msg.request.path || '');
    const statusCode = msg.response && msg.response.statusCode;
    dbg(`dc:undici:request:headers origin=${origin} path=${reqPath} status=${statusCode}`);

    // response.headers is a flat array [name0, value0, name1, value1, ...]
    const rawHeaders = msg.response && msg.response.headers;
    if (!Array.isArray(rawHeaders)) {
      dbg(`dc:headers unexpected type=${typeof rawHeaders}`);
      return;
    }

    // Log all anthropic-* headers for diagnostics (helps identify new header names)
    const anthropicHeaders = [];
    for (let i = 0; i < rawHeaders.length; i += 2) {
      const name = String(rawHeaders[i]).toLowerCase();
      if (name.startsWith('anthropic-')) {
        anthropicHeaders.push(`${name}=${String(rawHeaders[i + 1])}`);
      }
    }
    if (anthropicHeaders.length > 0) {
      dbg(`dc:anthropic-headers [${reqPath}]: ${anthropicHeaders.join(', ')}`);
    }

    const update = {};
    for (let i = 0; i < rawHeaders.length; i += 2) {
      const name = String(rawHeaders[i]).toLowerCase();
      const key  = HEADER_MAP[name];
      if (key) {
        const v = headerToValue(key, String(rawHeaders[i + 1]));
        if (v !== null) update[key] = v;
      }
    }
    applyUpdate(update);
  });

  dbg('diagnostics_channel: undici:request:headers subscribed');
} catch (e) {
  dbg(`diagnostics_channel unavailable: ${e.message}`);
}
```
