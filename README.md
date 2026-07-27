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
    - `mise run lint` or `pre-commit run -a`
- Slow checks (`l3build` tests)
  - `mise run test`: tests for actively maintained LaTeX packages
  - `mise run test-inactive`: tests for inactive LaTeX packages
- Misc check
  - `mise run lint:expl3 --inline-config 'stop_early_when_confused=false'`: deeper thus slower expl3 code linting
- Checks run on CI
  - [`lint.yml`](./.github/workflows/lint.yml) full quick checks (on Ubuntu)
  - [`check.yml`](./.github/workflows/check.yml) actively maintained slow checks (on Ubuntu)
  - [`schedule.yml`](./.github/workflows/schedule.yml)
    - run once a week
    - call `lint.yml`
    - call `check.yml` on 3 OSes, check inactive l3build tests in addition

### Tools

- `explcheck`: Development tools for expl3 programmers\
  https://github.com/Witiko/expltools \
  Installation: `tlmgr install expltools`
- `l3build`: A testing and building system for LaTeX\
  https://github.com/latex3/l3build\
  Installation: `tlmgr install l3build`
- `mise`: One tool that manages dev tools, env vars, and tasks per project\
  https://github.com/jdx/mise
- `pre-commit`: a Git hook framework\
  https://github.com/pre-commit/pre-commit \
  Installation: (recommended) `uv tool install pre-commit`
- `typos`: Source code spell checker\
  https://github.com/crate-ci/typos
- `uv`: An extremely fast Python package and project manager\
  https://github.com/astral-sh/uv
