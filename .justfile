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
all: lint test

lint: typos explcheck

test: test-zutil test-tabularray-all

test-tabularray-all: test-tabularray test-tabularray-old

# recipes
typos:
    @{{_info}}"Checking for typos..."{{_end_info}}
    {{_debug}} typos

explcheck:
    @{{_info}}"Checking for expl3 issues..."{{_end_info}}
    {{_debug}} explcheck support/*.cfg
    {{_debug}} explcheck zutil/*.sty zutil/*.tex
    # {{_debug}} explcheck --ignored-issues=s103,s204,w302 tabularray/tabularray.sty

_l3build-check package="" config="" +options="":
    @{{_info}}"Running" {{package}} "l3build tests"\
        {{ if config != "" { ', config \"' + config + '\"' } else {""} }}"..."\
        {{_end_info}}
    cd {{join(justfile_dir(), package)}} && \
        {{_debug}} l3build check -q --show-saves \
        {{ if config != "" { "-c" + config } else {""} }} \
        {{options}}

test-zutil options="" tests="": (_l3build-check "zutil" "" options tests)

# _test-tabularray config="" option="":
#     @{{_info}}"Running tabularray l3build tests" \
#         {{ if config != "" { ", config \"" + config + ".lua\"..." } \
#            else { "" } }} \
#         {{_end_info}}
#     cd {{justfile_dir()}}/tabularray && \
#         {{_debug}} l3build check -q --show-saves -c"{{config}}" {{option}}
#     @{{ if config == "config-old" \
#             { "cd " + justfile_dir() + "/tabularray && " + \
#                 _debug + " texlua buildend.lua" } \
#         else { "" } }}

test-tabularray +options="": (_l3build-check "tabularray" "build" options)

test-tabularray-old +options="": (_l3build-check "tabularray" "config-old" options)
    cd {{join(justfile_dir(), "tabularray")}} && \
        {{_debug}} texlua buildend.lua
