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

export diffext := env('diffext', '.diff')
export diffexe := env('diffexe', 'git diff --no-index --text --')

L3BUILD_CHECK_OPTIONS := env('L3BUILD_CHECK_OPTIONS', '-q --show-saves')
L3BUILD_SAVE_OPTIONS := env('L3BUILD_SAVE_OPTIONS', '-q')

## top-level recipes

# List all recipes
default:
    just --justfile {{justfile()}} --list --unsorted

[group('*meta')]
test: zutil

[group('*meta')]
test-inactive: tblr tblr-old tblr-ppm

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
