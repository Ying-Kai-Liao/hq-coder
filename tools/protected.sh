#!/bin/sh
# protected.sh <checkout> <branch> — is <branch> protected on GitHub? Read-only (one GET).
# Prints one line: "protected", "unprotected", or "unknown: <why>". Always exits 0.
# Reads .protected from the branch endpoint, which needs only read access (the protection endpoint needs admin).
dir=${1:?usage: protected.sh <checkout> <branch>}; branch=${2:?usage: protected.sh <checkout> <branch>}
repo=$(cd "$dir" 2>/dev/null && gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null) \
  || { echo "unknown: no GitHub repo for $dir (gh repo view failed)"; exit 0; }
p=$(gh api "repos/$repo/branches/$branch" -q .protected 2>/dev/null) \
  || { echo "unknown: gh api repos/$repo/branches/$branch failed"; exit 0; }
case $p in
  true)  echo "protected" ;;
  false) echo "unprotected" ;;
  *)     echo "unknown: unexpected answer '$p'" ;;
esac
