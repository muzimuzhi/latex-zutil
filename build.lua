bundle  = "latex-zutil"
module  = ""

-- optional, otherwise the auto-detection will take over, see
-- the `listmodules()` in `l3build-stdmain.lua`.
modules = { "zutil", "tabularray" }

--[[
`diffext` and `diffexe` MUST be set as envvars, not `l3build` variables.
See feature request https://github.com/latex3/l3build/issues/400.

For now these two envvars are set in `mise.toml` and taken into account if
`mise` is activated or when running `mise` tasks.

-- set OS-independent diff file extension and program
diffext = ".diff"
diffexe = "git diff --no-index --text --"
]]
