#!/usr/bin/env bash

# A script to update the CIPs list in README.md.
# If it works there will be no output - it edits the file directly.
# Requires: coreutils findutils git gnused jq pandoc

set -euo pipefail

cd "$(dirname "$0")/.."
pandoc_template="$(mktemp template.XXXXX.gfm)"
trap 'rm -f "$pandoc_template"' EXIT

get_last_update() {
  git log --date=local --format=%cs -1 -- CIP-*
}

all_metadata_jsonlines() {
  # shellcheck disable=SC2016
  echo '$for(sourcefile)${"sourcefile":"$sourcefile$","meta":$meta-json$}$endfor$' > "$pandoc_template"
  find CIP-* -type f -name 'CIP-*.md' | sort -n | while read -r cip; do
    pandoc --from=gfm --to=gfm --template="$pandoc_template" "$cip"
  done
}

table_lines() {
  jq --raw-output '"| \(.meta.CIP) | [\(.meta.Title)](./\(.sourcefile)) | \(.meta.Status) |"'
}

replace_table() {
  sed -i '/^|.----/,/^$/!b;//!d;0,/^|.----/r /dev/stdin' "$1"
  sed -i 's/(as of [^)]*)/(as of '"$(get_last_update)"')/' "$1"
}

all_metadata_jsonlines | table_lines | replace_table README.md
