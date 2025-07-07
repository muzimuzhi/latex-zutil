module = "zutil"


maindir         = ".."

sourcefiles     = { "*.sty", "*.tex" }
installfiles    = { "*.sty", "*.tex" }

checkengines    = { "pdftex", "xetex", "luatex" }
stdengine       = "pdftex"
checksuppfiles  = { "regression-test.cfg" }
