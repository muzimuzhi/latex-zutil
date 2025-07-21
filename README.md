# Z's LaTeX utilities

[![Check](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml)
[![Lint](https://github.com/muzimuzhi/latex-zutil/actions/workflows/lint.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/lint.yml)

## Components

- `./scripts/l3build.py`\
  A `l3build` wrapper which makes checking and saving `l3build` tests easier
- `./zutil`\
  Utility macros in expl3; documented in its own [README](./zutil/README.md).
- `./tabularray`\
  The [`tabularray`](https://ctan.org/pkg/tabularray) LaTeX package with experimental improvements (currently out-of-date)

## Development

### Checks

- Quick checks (various linters)
  - incremental run (on `git` staged files only)
    - auto triggered by `git commit` (`pre-commit` git hook in use)
    - run `pre-commit run` manually
  - full run
    - run `just lint-all` or `pre-commit run -a`
- Slow checks (`l3build` test suites)
  - run actively maintained test suites `just check zutil tblr`
  - run all test suites `just test-all`
- Full checks
  - run `just all`
- Checks run on CI
  - [`lint.yml`](./.github/workflows/lint.yml) full quick checks
  - [`check.yml`](./.github/workflows/check.yml) actively maintained slow checks (on Ubuntu)
  - [`schedule.yml`](./.github/workflows/schedule.yml) once a week, quick checks (on Ubuntu) + full slow checks on 3 OSes

### General `just` usages

```shell
# list all "just" available recipes
$ just
# list commands that would run by RECIPE
$ just -n/--dry-run RECIPE

# (just recipes `check` and `save` both use `l3build.py`)
# print help text of `l3build.py`
$ just [check|save] -h
# check/save one or more tests and/or testsuites
$ just check zutil tblr
$ just save zutil-001 tblr-loading
```

Note: As configured by `.justfile` in this repository, `just` invoked from any subdirectories acts the same as being invoked from the top-level directory.

### Tools

- `explcheck`: Development tools for expl3 programmers\
  https://github.com/Witiko/expltools \
  Installation: `tlmgr install expltools`
- `just`: Just a command runner\
  https://github.com/casey/just
- `l3build`: A testing and building system for LaTeX\
  https://github.com/latex3/l3build\
  Installation: `tlmgr install l3build`
- `pre-commit`: a Git hook framework\
  https://github.com/pre-commit/pre-commit \
  Installation: (recommended) `uv tool install pre-commit`
- `typos`: Source code spell checker\
  https://github.com/crate-ci/typos
- `uv`: An extremely fast Python package and project manager\
  https://github.com/astral-sh/uv
