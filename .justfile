# https://github.com/casey/just?tab=readme-ov-file
# use "just --dry-run [--verbose] <recipe>..." to check the actual commands
# run by the recipe(s)

# settings

set ignore-comments := true

# variables
_set_style := BOLD + GREEN
_reset_style := NORMAL
_info := "echo " + _set_style
_end_info := _reset_style

# default recipe

default:
    just --list

# meta recipes

all: && lint test-all

[group('lint')]
lint: && typos explcheck

[group('test')]
test-all: && (test "zutil") test-tabularray

[group('test')]
test-tabularray: && (test "tabularray" "build") (test "tabularray" "config-old")

# recipes

[group('lint')]
typos:
    @{{_info}}Checking for typos...{{_end_info}}
    typos

[group('lint')]
explcheck:
    @{{_info}}Checking for expl3 issues...{{_end_info}}
    explcheck support/*.cfg
    explcheck zutil/*.sty zutil/*.tex
    # explcheck --ignored-issues=s103,s204,w302 tabularray/tabularray.sty

[group('test')]
test package="" config="" +options="":
    @{{_info}}'Running {{package}} tests\
        {{ if config != "" { ', config "' + config + '"' } else {""} }}...'\
        {{_end_info}}
    cd {{package}} && \
        l3build check -q --show-saves \
            {{ if config != "" { "-c\"" + config + "\"" } else { "" } }} {{options}}
    {{ if package == "tabularray" { \
        if config == "config-old" { \
            "cd " + package + " && texlua buildend.lua" \
        } else { "" } \
    } else { "" } }}
