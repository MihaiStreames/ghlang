#!/usr/bin/env bash
set -euo pipefail

# Remove build artifacts, caches, and generated files
#
# Usage:
#   ./scripts/clean.sh            remove caches only
#   ./scripts/clean.sh --all      also remove dist/, bench/, and generated output

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

MODE="caches"
for arg in "$@"; do
    [[ "$arg" == "--all" ]] && MODE="all"
done

# ---------------------------------------------------------------------------
# caches
# ---------------------------------------------------------------------------
echo "Cleaning caches..."

find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

echo "  Removed __pycache__, .mypy_cache, .pytest_cache, .ruff_cache"

# ---------------------------------------------------------------------------
# build + bench artifacts (--all only)
# ---------------------------------------------------------------------------
if [[ "$MODE" == "all" ]]; then
    echo "Cleaning build artifacts..."

    rm -rf "$PROJECT_ROOT/dist"
    rm -rf "$PROJECT_ROOT/bench"
    rm -rf "$PROJECT_ROOT/build"
    find "$PROJECT_ROOT" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

    echo "  Removed dist/, bench/, build/, *.egg-info"
fi

echo "Done"
