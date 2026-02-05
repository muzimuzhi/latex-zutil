# Z's LaTeX utilities

[![Check](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/check.yml)
[![Lint](https://github.com/muzimuzhi/latex-zutil/actions/workflows/lint.yml/badge.svg)](https://github.com/muzimuzhi/latex-zutil/actions/workflows/lint.yml)

## Components

- `l3build-wrapper`\
  Check and save selective `l3build` tests easier
- `zutil`\
  Utility macros in expl3; documented in its [README](./zutil/README.md).
- `tabularray`\
  The [`tabularray`][ctan-tabularray] LaTeX package with experimental improvements (currently out-of-date)

[ctan-tabularray]: https://ctan.org/pkg/tabularray

## Development

### Checks

- Quick checks (various linters)
  - incremental run (on `git` staged files only)
    - auto triggered by `git commit` (`pre-commit` git hook in use), or
    - run `pre-commit run` manually
  - full run
    - `just lint` or `pre-commit run -a`
- Slow checks (`l3build` tests)
  - `just test`: tests for actively maintained LaTeX packages
  - `just test-inactive`: tests for inactive LaTeX packages
- Checks run on CI
  - [`lint.yml`](./.github/workflows/lint.yml) full quick checks and `just explcheck-slow` (on Ubuntu)
  - [`check.yml`](./.github/workflows/check.yml) actively maintained slow checks (on Ubuntu by default)
  - [`schedule.yml`](./.github/workflows/schedule.yml) once a week, `lint.yml` on Ubuntu + `check.yml` on 3 OSes

### General `just` usages

```shell
# list all "just" available recipes
$ just
# list commands that would run by RECIPE
$ just -n/--dry-run RECIPE

# (just recipes `check` and `save` both use `l3build_wrapper.py`)
# print help text of `l3build_wrapper.py`
$ just [check|save] -h
# check/save one or more tests and/or testsuites
$ just check zutil tblr
$ just save --all-engines zutil-001 tblr-loading
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
