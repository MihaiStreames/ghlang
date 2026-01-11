#!/usr/bin/env bash
set -euo pipefail

VERSION="$(grep -E '^pkgver=' PKGBUILD | cut -d= -f2)"
echo "Fetching ghlang-${VERSION}.tar.gz from PyPI"

curl -sL -o /tmp/ghlang-${VERSION}.tar.gz \
  https://files.pythonhosted.org/packages/source/g/ghlang/ghlang-${VERSION}.tar.gz
SHA=$(sha256sum /tmp/ghlang-${VERSION}.tar.gz | awk '{print $1}')

echo "SHA256: $SHA"
sed -i "s/^sha256sums=.*/sha256sums=('${SHA}')/" PKGBUILD
rm /tmp/ghlang-${VERSION}.tar.gz
