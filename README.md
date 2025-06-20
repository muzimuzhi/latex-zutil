# Z's LaTeX utility macros

## Development

### Project structure

```
# based on "tree -a -L2 -I .git -I .vscode"
.
├── .explcheckrc     # explcheck [1] config file
├── .gitattributes
├── .github
│   └── ...
├── .gitignore
├── .justfile        # just [2] definition file
├── README.md
├── _typos.toml      # typos [3] config file
├── build            # temp l3build [4] directory (if exist)
├── build.lua        # l3build config file
├── support          # l3build support files
│   └── ...
├── tabularray       # experimental tabularray development
│   ├── build.lua        # tabularray l3build config file
│   ├── buildend.lua     # wrapper to use support/ppmcheckpdf.lua
│   ├── config-old.lua   # tabularray l3build config file for old test set
│   ├── doc
│   ├── tabularray.sty
│   ├── testfiles        # new l3build test set
│   ├── testfiles-old    # old l3build test set   
│   └── ...
└── zutil            # experimental LaTeX utility macros
    ├── build.lua        # zutil l3build config file
    ├── testfiles        # zutil l3build tests
    ├── zutil-debug.code.tex
    ├── zutil-l3extras.code.tex
    ├── zutil-softerror.code.tex
    └── zutil.sty
```

## Linting and Testing

Tools

- [1] `explcheck`: Development tools for expl3 programmers\
      https://github.com/Witiko/expltools
- [2] `just`: Just a command runner\
      https://github.com/casey/just
- [3] `typos`: Source code spell checker\
      https://github.com/crate-ci/typos
- [4] `l3build`: A testing and building system for LaTeX\
      https://github.com/latex3/l3build

Commands

```
$ just
just --list --unsorted
Available recipes:
    default                             # Print all recipes

    [*meta]
    all
    lint-all                            # [alias: lint]
    test-all

    [test]
    zutil *options=""                   # Run zutil tests
    tabularray *options=""              # Run tabularray tests
    test package config="" *options=""  # Run l3build tests [alias: check]
    save package config="" *options=""  # Save l3build test results

    [lint]
    typos                               # Check typos
    explcheck                           # Check for expl3 issues
```

Run `just --dry-run <recipe>` to list commands run by each recipe
