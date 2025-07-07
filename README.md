# Z's LaTeX utility macros

[![Check](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml)
[![Lint](https://github.com/muzimuzhi/latex-zutil/actions/workflows/lint.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/lint.yml)

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
├── .pre-commit-config.yaml # pre-commit [3] config file
├── README.md
├── _typos.toml      # typos [4] config file
├── build            # temp l3build [5] directory (if exist)
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
      https://github.com/Witiko/expltools\
      Installation: `tlmgr install expltools`
- [2] `just`: Just a command runner\
      https://github.com/casey/just
- [3] `pre-commit`: a Git hook framework\
      https://github.com/pre-commit/pre-commit\
      Installation: (recommended) `uv tool install pre-commit`
- [4] `typos`: Source code spell checker\
      https://github.com/crate-ci/typos
- [5] `l3build`: A testing and building system for LaTeX\
      https://github.com/latex3/l3build\
      Installation: `tlmgr install l3build`

Checks

- Quick checks
  - check spelling, lint expl3 files, lint GitHub Actions workflow files, and more (see `.pre-commit-config.yaml`)
  - incremental run (on `git` staged files only)
    - auto triggered by `git commit` (`pre-commit` git hook in use)
    - run `pre-commit run`
  - full run
    - run `just lint-all` or `pre-commit run -a`
- Slow checks
  - `l3build` tests
  - run `just test-all`
- Full checks
  - run `just all`
- Checks on CI
  - [`lint.yml`](./.github/workflows/lint.yml) full quick checks
  - [`check.yml`](./.github/workflows/check.yml) full slow checks (on single OS)
  - [`schedule.yml`](./.github/workflows/schedule.yml) once a week, quick checks (on 1 OS) + slow checks on 3 OSes

General `just` usages

```shell
# list all "just" recipes available in this repo
$ just
# list commands that would run by RECIPE
$ just -n/--dry-run RECIPE
```

Note: As configured by `.justfile` in this repository, `just` can be invoked from any subdirectory and it acts the same.
