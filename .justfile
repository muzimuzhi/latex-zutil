# https://github.com/casey/just?tab=readme-ov-file
# https://just.systems/man/en/

# use "just --dry-run [--verbose] <recipe>..." to check the actual commands
# run by the recipe(s)


# settings
# https://github.com/casey/just?tab=readme-ov-file#settings

set ignore-comments := true


# variables

set_style := BOLD + BLUE
reset_style := NORMAL
info := "echo " + set_style + "'===>' "
end_info := reset_style

L3BUILD_CHECK_OPTIONS := env('L3BUILD_CHECK_OPTIONS', '-q --show-saves')

# default recipe

default:
    just --list


# meta recipes

all: && lint-all test-all

[group('lint')]
lint-all: && typos explcheck

[group('test')]
test-all: && (zutil) (tabularray "build") (tabularray "config-old")

[group('test')]
zutil +options="": && (test "zutil" "" options)

[group('test')]
tabularray config="build" +options="": && (test "tabularray" config options)

# simple recipes

[group('lint')]
typos:
    @{{ info }}Checking for typos...{{ end_info }}
    typos

[group('lint')]
explcheck:
    @{{ info }}Checking for expl3 issues...{{ end_info }}
    explcheck support/*.cfg
    explcheck zutil/*.sty zutil/*.tex
    # explcheck --ignored-issues=s103,s204,w302 tabularray/tabularray.sty

[group('test')]
test package="" config="" +options="":
    @{{ info }}'Running {{ package }} tests\
        {{ if config != "" { ', config "' + config + '"' } else { "" } }}...'\
        {{ end_info }}
    cd {{ package }} && \
        l3build check {{ L3BUILD_CHECK_OPTIONS }} \
            {{ if config != "" { "-c\"" + config + "\"" } else { "" } }} {{ options }}
    {{ if package == "tabularray" { \
        if config == "config-old" { \
            "cd " + package + " && texlua buildend.lua" \
        } else { "" } \
    } else { "" } }}
