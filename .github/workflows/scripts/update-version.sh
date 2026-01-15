#!/usr/bin/env bash
set -euo pipefail

VERSION="$1"
sed -i "s/^pkgver=.*/pkgver=${VERSION}/" PKGBUILD
