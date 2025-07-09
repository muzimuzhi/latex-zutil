# https://github.com/casey/just?tab=readme-ov-file
# https://just.systems/man/en/

# use "just --dry-run [--verbose] <recipe>" to check the actual commands
# that would run in <recipe>


# settings
# https://github.com/casey/just?tab=readme-ov-file#settings

set ignore-comments := true


## variables

info := BOLD + BLUE + "===> "
end_info := NORMAL

export SKIP := env('SKIP', 'typos,explcheck')
export diffext := env('diffext', '.diff')
export diffexe := env('diffexe', 'git diff --no-index --text --')

L3BUILD_CHECK_OPTIONS := env('L3BUILD_CHECK_OPTIONS', '-q --show-saves')
L3BUILD_SAVE_OPTIONS := env('L3BUILD_SAVE_OPTIONS', '-q')


## top-level recipes

# List all recipes
default:
    just --justfile {{justfile()}} --list --unsorted

[group('*meta')]
all: lint-all test-all

[group('*meta')]
lint-all: pre-commit typos explcheck

[group('*meta')]
test-all: zutil tabularray tabularray-old tabularray-ppm

alias lint := lint-all
alias test := test-all

## linting recipes

# Check spelling
[group('lint')]
typos *options="":
    @echo '{{ info }}Checking spelling...{{ end_info }}'
    typos {{ options }}

# Lint expl3 files
[group('lint')]
explcheck *options="":
    @echo '{{ info }}Linting expl3 files...{{ end_info }}'
    # this file list is composed in pre-commit config too
    explcheck {{ options }} support/*.cfg zutil/*.sty zutil/*.tex
    # explcheck --ignored-issues=s103,s204,w302 tabularray/tabularray.sty

alias expl3 := explcheck

# Run pre-commit checks on all files
[group('lint')]
pre-commit *options="":
    @echo '{{ info }}Running pre-commit checks...{{ end_info }}'
    @echo 'Skipped checks: {{ SKIP }}'
    pre-commit run --all-files {{ options }}


## testing recipes

# Run zutil tests
[group('test')]
zutil *options="":
    @echo '{{ info }}Checking zutil tests...{{ end_info }}'
    cd zutil && \
        l3build check {{ L3BUILD_CHECK_OPTIONS + " " + options }}

# Run tabularray tests, new config
[group('test')]
tabularray *options="":
    @echo '{{ info }}Checking tabularray tests, "build" config...{{ end_info }}'
    cd tabularray && \
        l3build check -c"build" {{ L3BUILD_CHECK_OPTIONS + " " + options }}

# Run tabularray tests, old config
[group('test')]
tabularray-old *options="":
    @echo '{{ info }}Checking tabularray tests, "config-old" config...{{ end_info }}'
    cd tabularray && \
        l3build check -c"config-old" {{ L3BUILD_CHECK_OPTIONS + " " + options }}

# Run tabularray PPM tests
[group('test')]
tabularray-ppm:
    @echo '{{ info }}Running tabularray PPM tests, "config-old" config...{{ end_info }}'
    cd tabularray && texlua buildend.lua

alias tblr := tabularray
alias tblr-old := tabularray-old
alias tblr-ppm := tabularray-ppm


# Check l3build test(s)
[group('dev')]
check *options="": (_l3build_single "check" options)

# Save l3build test(s)
[group('dev')]
save *options="": (_l3build_single "save" options)

_l3build_single command *options="":
    @echo '{{ info }}Running l3build {{ command }}...{{ end_info }}'
    @./scripts/l3build.py {{ command }} {{ options }}
