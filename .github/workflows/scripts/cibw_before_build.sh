#!/usr/bin/env bash
set -euo pipefail

if ! command -v rustup >/dev/null 2>&1; then
  curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
fi

if [ -f "$HOME/.cargo/env" ]; then
  . "$HOME/.cargo/env"
fi

target=""
tag=""
case "${CIBW_BUILD:-}" in
  *"manylinux_x86_64"*|*"linux_x86_64"*|*"musllinux_x86_64"*)
    target="x86_64-unknown-linux-gnu"
    tag="linux-x86_64"
    ;;
  *"manylinux_aarch64"*|*"linux_aarch64"*|*"musllinux_aarch64"*)
    target="aarch64-unknown-linux-gnu"
    tag="linux-aarch64"
    ;;
  *"win_amd64"*)
    target="x86_64-pc-windows-msvc"
    tag="windows-x86_64"
    ;;
esac

if [ -n "$target" ]; then
  rustup target add "$target"
  export CARGO_BUILD_TARGET="$target"
  export GHLANG_PLATFORM_TAG="$tag"
  cargo build --manifest-path tokount/Cargo.toml --release --target "$target"
else
  cargo build --manifest-path tokount/Cargo.toml --release
fi
python .github/workflows/scripts/copy_tokount_binary.py
