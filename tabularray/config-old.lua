testfiledir     = "testfiles-old"

-- overwrite configs inherited from "tabularray/build.lua"
checkengines    = { "pdftex" }
checksuppfiles  = { }

lvtext          = ".tex"

-- workaround https://github.com/latex3/l3build/issues/403
test_types = test_types or {} -- needed by ppm checks "texlua buildend.lua"
test_types.log = {
  test = lvtext,
  generated = logext,
  reference = tlgext,
  expectation = lveext,
  compare = compare_tlg,
  rewrite = rewrite_log,
}
