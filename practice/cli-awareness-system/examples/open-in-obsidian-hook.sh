#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Open in Obsidian — PostToolUse hook (matcher: "Write")
# ═══════════════════════════════════════════════════════════════════════════
# When Claude creates a .md file inside your vault, it opens in Obsidian.
# ═══════════════════════════════════════════════════════════════════════════

# ╔═══════════════════════════════════════════════════════════════╗
# ║  CUSTOMIZE: your Obsidian vault path and name                ║
# ╚═══════════════════════════════════════════════════════════════╝
VAULT_ROOT="/path/to/your/obsidian/vault"
VAULT_NAME="your-vault-name"

# Read tool output from stdin
fp=$(jq -r '.tool_input.file_path // empty')

# Only open .md files inside the vault
if [[ "$fp" == *.md ]] && [[ -f "$fp" ]] && [[ "$fp" == "$VAULT_ROOT"/* ]]; then
    relative="${fp#$VAULT_ROOT/}"
    encoded=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$relative'))")
    open "obsidian://open?vault=$VAULT_NAME&file=$encoded" 2>/dev/null
fi

exit 0
