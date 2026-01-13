#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

(
  cd "$repo_root/tokount"
  cargo build --release
)

export PATH="$repo_root/tokount/target/release:$PATH"

cd "$repo_root"
if [[ $# -gt 0 ]]; then
  uv run python -m ghlang.cli "$@"
else
  uv run python -m ghlang.cli
fi
