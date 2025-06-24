bundle  = "latex-zutil"
module  = ""

--[[
Unfortunately, "diffext" and "diffexe" MUST be set as envvars, not "l3build"
variables. See feature request https://github.com/latex3/l3build/issues/400.

For now these two envvars are set in `.justfile`, thus only take effect when
calling "l3build" via "just".

-- set OS-independent diff file extension and program
diffext = ".diff"
diffexe = "git diff --no-index --text --"
]]

checkbundles    = { "tabularray", "zutil" }
ctanbundles     = { "tabularray", "zutil" }
