#!/bin/bash

# Fix trailing whitespace and ensure files end with a newline
# Only process text files, skip binary files
find . -type f -not -path "*/\.*" -not -path "*/node_modules/*" -not -path "*/venv/*" -exec file {} \; | grep "text" | cut -d: -f1 | xargs -I{} sh -c '
  # Remove trailing whitespace
  LC_ALL=C sed -i "" -e "s/[[:space:]]*$//" "$1" 2>/dev/null || true

  # Ensure file ends with exactly one newline
  if [ -s "$1" ]; then
    # Check if file ends with newline
    if [ "$(tail -c 1 "$1" | wc -l)" -eq 0 ]; then
      # Add a newline if missing
      echo "" >> "$1"
    fi
  fi
' sh {} \;

echo "Formatting fixed for all text files"
