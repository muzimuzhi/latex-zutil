#!/usr/bin/env -S usage bash
#MISE description="Lint expl3 code"
#USAGE arg "[option]..." help="extra explcheck options and/or files"
#USAGE flag "--slow" default=#false help="force slow flow analysis"

# https://github.com/casey/just?tab=readme-ov-file#constants
NORMAL='\e[0m'
BOLD='\e[1m'
BLUE='\e[34m'

info() {
    echo -e "${BOLD}${BLUE}===> $1${NORMAL}"
}

if [[ "${usage_slow?}" == "true" ]]; then
    info "Patching explcheck config..."
    awk '
      {
        sub(/^# stop_(after|early_when_confused) = .*$/, substr($0, 3));
        print
      }
    ' "$EXPLCHECK_CONFIG" > "$EXPLCHECK_CONFIG".tmp
    cp "$EXPLCHECK_CONFIG" "$EXPLCHECK_CONFIG".bak
    mv "$EXPLCHECK_CONFIG".tmp "$EXPLCHECK_CONFIG"

    cleanup() {
        info "Restoring explcheck config..."
        mv "$EXPLCHECK_CONFIG".bak "$EXPLCHECK_CONFIG"
    }
    trap 'cleanup' EXIT
fi

if [[ "${usage_slow?}" == "true" ]]; then
    info "Linting expl3 code (slow)..."
else
    info "Linting expl3 code..."
fi

eval "options=($usage_option)"
# the glob file list is composed in pre-commit config too
explcheck \
    --config-file="$EXPLCHECK_CONFIG" \
    "${options[@]}" \
    zutil/*.sty zutil/*.tex support/*.cfg
# explcheck --ignored-issues=s103,s204,w302 "${options[@]}" tabularray/tabularray.sty
