#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

python_bin=${PYTHON:-python}
python_bin=$(command -v "$python_bin")

uv pip install --upgrade --python "$python_bin" build

cargo build --manifest-path tokount/Cargo.toml --release
.github/workflows/scripts/copy_tokount_binary.py

rm -rf dist
"$python_bin" -m build --wheel

uv pip install dist/*.whl --force-reinstall

"$python_bin" -c "import ghlang; print('ghlang import ok')"
if command -v ghlang >/dev/null 2>&1; then
  ghlang --help >/dev/null
  echo "ghlang --help ok"
fi
