#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
if ! command -v docker >/dev/null 2>&1; then
  echo "docker CLI not found in container; mount it or install docker.io" >&2
  exit 1
fi

uv build --sdist --out-dir dist --clear

export CIBW_BEFORE_BUILD="bash .github/workflows/scripts/cibw_before_build.sh"
export CIBW_BUILD=${CIBW_BUILD:-"cp310-* cp311-* cp312-* cp313-*"}
export CIBW_REPAIR_WHEEL_COMMAND=""
export CIBW_SKIP=${CIBW_SKIP:-"*musllinux*"}

uv tool run cibuildwheel --output-dir dist
