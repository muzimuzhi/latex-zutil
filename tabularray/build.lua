module = "tabularray"


maindir         = ".."
checkdeps       = { maindir .. "/zutil" }

sourcefiles     = { "tabularray.sty" }

-- "checkengines" and "checksuppfiles" will be overwritten in "config-old.lua"
checkengines    = { "pdftex", "xetex", "luatex" }
stdengine       = "pdftex"
checkruns       = 2
checksuppfiles  = { "zutil-regression-test.cfg" }


-- TODO: uncomment this when `tabularray` resumes updates. Last release was
--       2025C (2025-11-27).
-- checkconfigs    = { "build", "config-old" }

dofile(maindir .. "/support/build-normalize-log.lua")
