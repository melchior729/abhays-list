set shell := ["bash", "-cu"]

# Refresh solved progress from local neetcode-submissions clone
update:
    npm run generate

# Copy all pattern lists (path order, ✓ = solved) to clipboard
copy-list:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp)
    npx tsx scripts/copy-list.ts > "$tmp"
    cat "$tmp"
    if command -v wl-copy >/dev/null 2>&1; then
      cat "$tmp" | wl-copy 2>/dev/null || true
      sleep 0.2
      echo ""
      echo "Copied to clipboard (wl-copy)."
    fi
    rm -f "$tmp"
