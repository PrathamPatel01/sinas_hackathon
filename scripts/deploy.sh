#!/usr/bin/env bash
# Build the config and apply it to the Sinas instance.
#   ./scripts/deploy.sh --dry-run    preview changes
#   ./scripts/deploy.sh              apply for real
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "No .env found. Copy .env.example to .env and fill in SINAS_URL + SINAS_TOKEN." >&2
  exit 1
fi

python3 -m pip install --quiet pyyaml >/dev/null 2>&1 || true

if [ "${1:-}" = "--dry-run" ]; then
  python3 scripts/build_config.py --dry-run
else
  python3 scripts/build_config.py --apply
  echo
  echo "Applied. Next: python3 scripts/seed_corpus.py   (load the regulation store)"
fi
