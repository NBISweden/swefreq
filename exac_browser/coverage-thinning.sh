#!/bin/bash

set -e

mkdir coverage-thinned

for cov in coverage/Panel*.gz; do
    printf 'Processing "%s"... ' "$cov" >&2

    printf 'unzip... ' >&2
    tmpcov="$( mktemp -p . )"
    gzip -d -c "$cov" >"$tmpcov"

    printf 'filter... ' >&2
    head -n 1 "$tmpcov" >"$tmpcov".head
    sed '1d' "$tmpcov" | awk '$2 % 10 == 0 { print }' >"$tmpcov".data

    printf 'compress... ' >&2
    cat "$tmpcov".head "$tmpcov".data | bgzip >coverage-thinned/"${cov##*/}"

    printf 'index... ' >&2
    tabix -f -s 1 -b 2 -e 2 coverage-thinned/"${cov##*/}"

    printf 'done.\n' >&2
    rm -f "$tmpcov" "$tmpcov".head "$tmpcov".data
done
