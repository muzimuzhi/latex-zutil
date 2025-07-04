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

PRE_COMMIT_SKIP := env('PRE_COMMIT_SKIP', 'typos,explcheck')

diffext := env('diffext', '.diff')
diffexe := env('diffexe', 'git diff --no-index --text --')

L3BUILD_ENVS := 'diffext="' + diffext + '" diffexe="' + diffexe + '"'

L3BUILD_CHECK_OPTIONS := env('L3BUILD_CHECK_OPTIONS', '-q --show-saves')
L3BUILD_SAVE_OPTIONS := env('L3BUILD_SAVE_OPTIONS', '-q')

## default recipe

# Print all recipes
default:
    just --justfile {{justfile()}} --list --unsorted

## meta recipes

[group('*meta')]
all: && lint-all test-all

[group('*meta')]
lint-all: && (pre-commit "--all-files") (typos) (explcheck)

alias lint := lint-all

[group('*meta')]
test-all *options="": && (zutil options) (tabularray options)

# Run zutil tests
[group('test')]
zutil *options="": && (l3build-check "zutil" "" options)

# Run tabularray tests
[group('test')]
tabularray *options="": && \
    (l3build-check "tabularray" "build" options) \
    (l3build-check "tabularray" "config-old" options)

## simple recipes

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

# Run pre-commit checks
[group('lint')]
pre-commit *options="":
    @echo '{{ info }}Running pre-commit checks...{{ end_info }}'
    SKIP="{{ PRE_COMMIT_SKIP }}" pre-commit run {{ options }}

# Run l3build tests
[group('test')]
l3build-check package config="" *options="":
    @echo '{{ info }}Running {{ package }} tests\
        {{ if config != "" { ", config \"" + config + "\"" } else { "" } }}...\
        {{ end_info }}'
    cd {{ package }} && \
        {{ L3BUILD_ENVS }} l3build check {{ L3BUILD_CHECK_OPTIONS }} \
            {{ if config != "" { "-c\"" + config + "\"" } else { "" } }} {{ options }}
    {{ if package == "tabularray" { \
        if config == "config-old" { \
            "cd " + package + " && texlua buildend.lua" \
        } else { "" } \
    } else { "" } }}

alias check := l3build-check
alias test := l3build-check

# Save l3build test results
[group('test')]
l3build-save package config="" *options="":
    @echo '{{ info }}Running {{ package }} tests\
        {{ if config != "" { ", config \"" + config + "\"" } else { "" } }}...\
        {{ end_info }}'
    cd {{ package }} && \
        l3build save {{ L3BUILD_SAVE_OPTIONS }}\
            {{ if config != "" { "-c\"" + config + "\"" } else { "" } }} {{ options }}

alias save := l3build-save
