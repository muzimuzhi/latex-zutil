# https://github.com/casey/just?tab=readme-ov-file
# https://just.systems/man/en/

# use "just --dry-run [--verbose] <recipe>" to check the actual commands
# that would run in <recipe>

# settings
# https://github.com/casey/just?tab=readme-ov-file#settings

set ignore-comments := true
set unstable

## variables

info := BOLD + BLUE + "===> "
end_info := NORMAL

export SKIP := env('SKIP', 'typos,explcheck,ruff')
export diffext := env('diffext', '.diff')
export diffexe := env('diffexe', 'git diff --no-index --text --')

export EXPLCHECK_CONFIG := env('EXPLCHECK_CONFIG', 'config/explcheck.toml')

L3BUILD_CHECK_OPTIONS := env('L3BUILD_CHECK_OPTIONS', '-q --show-saves')
L3BUILD_SAVE_OPTIONS := env('L3BUILD_SAVE_OPTIONS', '-q')

## top-level recipes

# List all recipes
default:
    just --justfile {{justfile()}} --list --unsorted

[group('*meta')]
all: lint test

[group('*meta')]
lint: pre-commit typos explcheck ruff

[group('*meta')]
test: zutil

[group('*meta')]
test-inactive: tblr tblr-old tblr-ppm

## linting recipes

# Check spelling
[group('lint')]
typos *options="":
    @echo '{{ info }}Checking spelling...{{ end_info }}'
    typos --config=config/typos.toml {{ options }}

## per recipe attribute [env(NAME, VALUE)] needs just newer than 1.46.0
## https://github.com/casey/just/commit/c85bf9dd9a20a36e2e164b9f31740eb200d482c9

# Lint expl3 files
[group('lint')]
explcheck *options="":
    @echo '{{ info }}Linting expl3 code...{{ end_info }}'
    # this file list is composed in pre-commit config too
    explcheck \
        --config-file="$EXPLCHECK_CONFIG" \
        {{ options }} \
        zutil/*.sty zutil/*.tex support/*.cfg
    # explcheck --ignored-issues=s103,s204,w302 {{ options }} tabularray/tabularray.sty

# Lint expl3 files, flow analysis enabled
[group('lint')]
explcheck-slow *options="":
    #!/usr/bin/env -S bash
    echo '{{ info }}Patching config...{{ end_info }}'
    awk '{ sub(/^# stop_(after|early_when_confused) = .*$/, substr($0, 3)); print}' "$EXPLCHECK_CONFIG" > "$EXPLCHECK_CONFIG".tmp
    cp "$EXPLCHECK_CONFIG" "$EXPLCHECK_CONFIG".bak
    mv "$EXPLCHECK_CONFIG".tmp "$EXPLCHECK_CONFIG"

    cleanup() {
        echo '{{ info }}Restoring config...{{ end_info }}'
        mv "$EXPLCHECK_CONFIG".bak "$EXPLCHECK_CONFIG"
    }
    trap 'cleanup' EXIT

    echo '{{ info }}Linting expl3 code (slow)...{{ end_info }}'
    explcheck \
        --config-file="$EXPLCHECK_CONFIG" \
        {{ options }} \
        zutil/*.sty zutil/*.tex support/*.cfg

alias expl := explcheck
alias expl3 := explcheck
alias expl-slow := explcheck-slow
alias expl3-slow := explcheck-slow

# Run pre-commit checks on all files
[group('lint')]
pre-commit *options="":
    @echo '{{ info }}Running pre-commit checks...{{ end_info }}'
    @echo 'Skipped checks: {{ SKIP }}'
    pre-commit run --all-files {{ options }}

[group('lint')]
ruff command="check" *options="":
    @echo '{{ info }}Linting python code...{{ end_info }}'
    # `uvx` is an alias for `uv tool run`
    cd l3build-wrapper && uvx --isolated ruff {{ command }} {{ options }}

## testing recipes

# Run zutil l3build tests
[group('test')]
zutil: (check "zutil")

# Run tblr l3build tests
[group('test')]
tblr: (check "tblr")

# Run tblr old l3build tests
[group('test')]
tblr-old: (check "tblr-old")

# Run tabularray PPM tests
[group('test')]
tblr-ppm:
    @echo '{{ info }}Running tabularray PPM tests, "config-old" config...{{ end_info }}'
    cd tabularray && texlua buildend.lua

## development recipes

# Check l3build test(s)
[group('dev')]
check *options="": (_l3build_wrapper "check" L3BUILD_CHECK_OPTIONS options)

# Save l3build test(s)
[group('dev')]
save *options="": (_l3build_wrapper "save" L3BUILD_SAVE_OPTIONS options)

_l3build_wrapper command *options="":
    @echo '{{ info }}Running l3build_wrapper...{{ end_info }}'
    l3build-wrapper {{ command }} {{ options }}

# Create a new l3build test from template
[group('dev')]
new-test module name:
    #!/usr/bin/env -S bash
    echo '{{ info }}Creating new l3build test "{{ module }}-{{ name }}" for module "{{ module }}"...{{ end_info }}'
    template="support/TEMPLATE-{{ module }}-test.lvt"
    new_test="{{ module }}/testfiles/{{ module }}-{{ name }}.lvt"
    if [[ ! -f "$template" ]]; then
        echo "Template file \"$template\" does not exist."
        exit 1
    fi
    if [[ -f "$new_test" ]]; then
        echo "Test file \"$new_test\" already exists. Please choose a different name."
        exit 1
    fi
    cp "$template" "$new_test"
    code "$new_test"

# Reinstall l3build-wrapper in editable mode
[group('dev')]
install-wrapper:
    @echo '{{ info }}Reinstalling l3build-wrapper in editable mode...{{ end_info }}'
    cd l3build-wrapper && uv tool install --reinstall -e .
