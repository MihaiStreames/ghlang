#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

MODE="caches"
for arg in "$@"; do
  [[ "$arg" == "--all" ]] && MODE="all"
done

echo "Cleaning caches..."

find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".ty_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

echo "  Removed __pycache__, .ty_cache, .pytest_cache, .ruff_cache"

if [[ "$MODE" == "all" ]]; then
  echo "Cleaning build artifacts..."

  rm -rf "$PROJECT_ROOT/dist"
  rm -rf "$PROJECT_ROOT/bench"
  rm -rf "$PROJECT_ROOT/build"
  find "$PROJECT_ROOT" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

  echo "  Removed dist/, bench/, build/, *.egg-info"
fi

echo "Done"
