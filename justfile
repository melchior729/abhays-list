set shell := ["bash", "-cu"]

# Refresh solved progress from local neetcode-submissions clone
update:
    npm run generate

# copy all files to clipboard with borders (name, path, contents) via wl-copy
copy:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp)
    # find all files, excluding git, deps, build artifacts
    find . -type f \
      -not -path './.git/*' \
      -not -path './node_modules/*' \
      -not -path './.next/*' \
      -not -path './.vercel/*' \
      -not -name '*.lock' \
      -not -name 'package-lock.json' \
      -print0 | sort -z | while IFS= read -r -d '' f; do
        if file --mime "$f" | grep -q "binary"; then
          continue
        fi
        name=$(basename "$f")
        {
          echo "┌────────────────────────────────────────────────────────────"
          echo "│ File: $name"
          echo "│ Path: $f"
          echo "└────────────────────────────────────────────────────────────"
          cat "$f"
          echo ""
          echo ""
        } >> "$tmp"
    done
    # pipe to wl-copy (Wayland clipboard) - fork to avoid blocking shell exit
    if command -v wl-copy >/dev/null 2>&1; then
      cat "$tmp" | wl-copy 2>/dev/null || true
      # wl-copy forks and stays alive; detach so `just` exits cleanly
      sleep 0.2
    else
      echo "wl-copy not found, printing to stdout instead:"
      cat "$tmp"
    fi
    echo "Copied $(wc -l < "$tmp") lines from $(grep -c "^┌" "$tmp") files to clipboard (wl-copy)."
    rm -f "$tmp"
