#!/usr/bin/env -S bash
#MISE description="Check expl3 code"
#USAGE arg "[option]..." help="extra explcheck options and/or files"
#USAGE flag "--slow" default=#false help="force slow flow analysis"
info() {
    echo -e "${INFO}$1${END_INFO}"
}

if [[ "${usage_slow?}" == "true" ]]; then
    info "Patching config..."
    awk '{ sub(/^# stop_(after|early_when_confused) = .*$/, substr($0, 3)); print}' \
        "$EXPLCHECK_CONFIG" > "$EXPLCHECK_CONFIG".tmp
    cp "$EXPLCHECK_CONFIG" "$EXPLCHECK_CONFIG".bak
    mv "$EXPLCHECK_CONFIG".tmp "$EXPLCHECK_CONFIG"

    cleanup() {
        info "Restoring config..."
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
