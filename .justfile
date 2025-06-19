# https://github.com/casey/just?tab=readme-ov-file
# https://just.systems/man/en/

# use "just --dry-run [--verbose] <recipe>..." to check the actual commands
# run by the recipe(s)


# settings
# https://github.com/casey/just?tab=readme-ov-file#settings

set ignore-comments := true


# variables

[private]
_set_style := BOLD + BLUE
[private]
_reset_style := NORMAL
[private]
_info := "echo " + _set_style + "'===>' "
[private]
_end_info := _reset_style


# default recipe

default:
    just --list


# meta recipes

all: && lint-all test-all

[group('lint')]
lint-all: && typos explcheck

[group('test')]
test-all: && zutil tabularray

[group('test')]
zutil: && (l3build-check "zutil")

[group('test')]
tabularray: && (l3build-check "tabularray" "build") \
    (l3build-check "tabularray" "config-old")


# simple recipes

[group('lint')]
typos:
    @{{ _info }}Checking for typos...{{ _end_info }}
    typos

[group('lint')]
explcheck:
    @{{ _info }}Checking for expl3 issues...{{ _end_info }}
    explcheck support/*.cfg
    explcheck zutil/*.sty zutil/*.tex
    # explcheck --ignored-issues=s103,s204,w302 tabularray/tabularray.sty

[group('test')]
l3build-check package="" config="" +options="":
    @{{ _info }}'Running {{ package }} tests\
        {{ if config != "" { ', config "' + config + '"' } else { "" } }}...'\
        {{ _end_info }}
    cd {{ package }} && \
        l3build check -q --show-saves \
            {{ if config != "" { "-c\"" + config + "\"" } else { "" } }} {{ options }}
    {{ if package == "tabularray" { if config == "config-old" { "cd " + package + " && texlua buildend.lua" } else { "" } } else { "" } }}
