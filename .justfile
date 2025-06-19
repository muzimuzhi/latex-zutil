# settings

set ignore-comments := true

# variables

_typos := require("typos")
_explcheck := require("explcheck")

debug := "false"
_debug := if debug != "false" { "echo" } else { "" }

_set_style := BOLD + GREEN
_reset_style := NORMAL
_info := "echo " + _set_style
_end_info := _reset_style

# default recipe

default:
    just --list

# meta recipes

all: lint-all test-all

[group('lint')]
lint-all: typos explcheck

[group('test')]
test-all: (test "zutil") test-tabularray

[group('test')]
test-zutil: (test "zutil")

[group('test')]
test-tabularray: (test "tabularray" "build") (test "tabularray" "config-old")

# recipes

[group('lint')]
typos:
    @{{_info}}"Checking for typos..."{{_end_info}}
    {{_debug}} typos

[group('lint')]
explcheck:
    @{{_info}}"Checking for expl3 issues..."{{_end_info}}
    {{_debug}} explcheck support/*.cfg
    {{_debug}} explcheck zutil/*.sty zutil/*.tex
    # {{_debug}} explcheck --ignored-issues=s103,s204,w302 tabularray/tabularray.sty

[group('test')]
test package="" config="" +options="":
    @{{_info}}"Running" {{package}} "tests"\
        {{ if config != "" { ', config \"' + config + '\"' } else {""} }}"..."\
        {{_end_info}}
    {{_debug}} cd {{join(justfile_dir(), package)}} && \
        {{_debug}} l3build check -q --show-saves \
        {{ if config != "" { "-c" + config } else {""} }} \
        {{options}}
    {{ if package == "tabularray" { \
        if config == "config-old" { \
            _debug + " cd " + join(justfile_dir(), package) + " && " + \
                _debug + " texlua buildend.lua" \
        } else { "" } \
    } else { "" } }}
