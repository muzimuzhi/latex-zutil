# Z's LaTeX utility macros

[![Test suite](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml)

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
│   ├── CONTRIBUTING.md
│   ├── README.md
│   ├── build.lua        # tabularray l3build config file
│   ├── buildend.lua     # wrapper to use support/ppmcheckpdf.lua
│   ├── config-old.lua   # tabularray l3build config file for old test set
│   ├── doc
│   ├── tabularray.sty
│   ├── testfiles        # new l3build test set
│   ├── testfiles-old    # old l3build test set   
│   └── ...
└── zutil            # experimental LaTeX utility macros
    ├── README.md
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

Run all checks locally, as on [CI](./.github/workflows/check.yml)
```shell
$ just all
```

General `just` usages

```shell
# list all "just" recipes/commands
$ just
# list shell commands that would run by a "just" recipe
$ just --dry-run <recipe>
```

Advanced `just` usages in this repository

```shell
# fix typos in-place
$ just typos -w/--write-changes
# or "typos -w/--write-changes"

# check l3build tests using "latex-dev"
$ just test-all --dev

# save a l3build test
$ just save tabularray build tblr-zutil-debug

# check a l3build test
$ just check tabularray build tblr-zutil-debug
```

Note: As configured by `.justfile` in this repository, `just` can be invoked from any subdirectory and it acts the same.
