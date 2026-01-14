#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if command -v docker >/dev/null 2>&1; then
  docker run --rm -v "$repo_root":/repo -w /repo archlinux:latest bash -lc '
    pacman -Sy --noconfirm base-devel git rust cargo python-build python-installer python-hatchling
    useradd -m builder
    chown -R builder:builder /repo
    su - builder -c "cd /repo && bash docker/ci_aur.sh"
  '
  exit 0
fi

pkgver=$(grep -E "^pkgver=" PKGBUILD | cut -d= -f2)
tarball="/repo/dist/ghlang-${pkgver}.tar.gz"

if [ -f "$tarball" ]; then
  tmp_dir=$(mktemp -d)
  cp PKGBUILD "$tmp_dir/PKGBUILD"
  sha256=$(sha256sum "$tarball" | awk "{print \$1}")
  sed -i "s|^source=.*|source=(\"file://${tarball}\")|g" "$tmp_dir/PKGBUILD"
  sed -i "s|^sha256sums=.*|sha256sums=('${sha256}')|g" "$tmp_dir/PKGBUILD"
  chown -R builder:builder "$tmp_dir"
  su - builder -c "cd \"$tmp_dir\" && makepkg --syncdeps --noconfirm --cleanbuild"
  rm -rf "$tmp_dir"
else
  chown -R builder:builder /repo
  su - builder -c "cd /repo && makepkg --syncdeps --noconfirm --cleanbuild"
fi
