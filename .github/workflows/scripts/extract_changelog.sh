#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"
CHANGELOG="${2:-CHANGELOG.md}"

[[ -z "$VERSION" ]] && exit 1
[[ ! -f "$CHANGELOG" ]] && exit 1

# strip leading 'v' if present so v2.5.5 and 2.5.5 both match
VERSION="${VERSION#v}"

# extract section for this version in Keep-a-Changelog format:
# starts at '## [VERSION]', stops at next '## [' header
section="$(awk -v ver="$VERSION" '
    /^## \[/ {
        if (found) exit
        if (index($0, "[" ver "]")) { found=1; next }
    }
    found { print }
' "$CHANGELOG" \
	| sed -e :a -e '/^[[:space:]]*$/{ $d; N; ba; }')"

if [[ -z "$section" ]]; then
    echo "failed to extract release notes for '$VERSION' from $CHANGELOG" >&2
    exit 1
fi

printf '%s\n' "$section"
