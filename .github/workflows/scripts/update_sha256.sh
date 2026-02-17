#!/usr/bin/env bash
set -euo pipefail

TARBALL=$(ls dist/*.tar.gz)
SHA=$(sha256sum "$TARBALL" | awk '{print $1}')

echo "SHA256: $SHA"
sed -i "s|^sha256sums=.*|sha256sums=('${SHA}')|" PKGBUILD

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
	echo "sha256=$SHA" >>"$GITHUB_OUTPUT"
fi
