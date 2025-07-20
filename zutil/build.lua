module = "zutil"


maindir         = ".."

sourcefiles     = { "*.sty", "*.tex" }
installfiles    = { "*.sty", "*.tex" }

checkengines    = { "pdftex", "xetex", "luatex" }
stdengine       = "pdftex"
checksuppfiles  = { "zutil-regression-test.cfg" }

-- show message of expandable errors as full as possible
-- these are the maximum values accepted by the TeX Live, see texmf.cnf
--
-- setting them in the top-level `build.lua` file doesn't work, because
-- running `l3build` in `./zutil` won't even load the top-level `build.lua`.
errorline       = 254
halferrorline   = 239

dofile(maindir .. "/support/build-normalize-log.lua")
