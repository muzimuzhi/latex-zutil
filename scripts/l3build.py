#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# Python 3.12 is needed by the `type` alias statement.
# Required python version is also recorded in `ruff.toml`.

"""An l3build wrapper to check and save l3build tests easier."""

import argparse
import os
import sys
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Final

type Test = str


class TestSuite:
    """A l3build test suite."""

    def __init__(
        self,
        name: str,
        path: str,
        config: str,
        tests: list[Test],
        alias: str | None = None,
    ) -> None:
        self.name = name
        self.alias = alias
        self.path = path
        self.config = config
        self.tests = tests
        self.test_names: tuple[Test, ...] | None = None

    def get_names(self) -> tuple[Test, ...]:
        """Generate test names from the test patterns."""
        if self.test_names is not None:
            return self.test_names

        test_names = []
        for test in self.tests:
            test_names.extend([p.stem for p in Path(self.path).glob(test)])
        self.test_names = tuple(test_names)
        return self.test_names


class TestSuiteRun:
    """Data needed by running l3build on a single test suite."""

    def __init__(self, ts: TestSuite) -> None:
        self.name = ts.name
        self.ts = ts
        self.options: list[str] = []
        self.names: list[Test] = []
        self.run_as_whole: bool = False

    def add_name(self, name: Test) -> None:
        """Add a test name to the test suite run."""
        if name not in self.names:
            self.names.append(name)

    def _add_option(self, option: str) -> None:
        self.options.append(option)

    def finalize_names(self, args: argparse.Namespace) -> None:
        """Adjust collected test names at final stage."""
        if self.run_as_whole:
            # `save` a testsuite means saving all names in it
            if args.target == 'save':
                self.names = list(self.ts.get_names())
            # `check` a testsuite means checking with no names
            elif args.target == 'check':
                self.names = []

    def set_options(self, args: argparse.Namespace) -> None:  # noqa: C901
        """Compose l3build options."""
        if self.ts.config:
            self._add_option(f'-c{self.ts.config}')
        if args.engine:
            self._add_option(f'-e{args.engine}')
        if args.stdengine:
            self._add_option('-s')
        if args.quiet:
            self._add_option('-q')
        if args.verbose and not on_ci():
            self._add_option('-v')
        if args.halt_on_error:
            self._add_option('-H')
        if args.target == 'check' and args.show_saves:
            self._add_option('-S')
        if args.dev:
            self._add_option('--dev')
        if args.dirty:
            self._add_option('--dirty')
        if args.show_log_on_error:
            self._add_option('--show-log-on-error')


zutil = TestSuite(
    name='zutil',
    path='zutil',
    config='build',
    tests=['testfiles/*.lvt'],
)

tblr = TestSuite(
    name='tabularray',
    alias='tblr',
    path='tabularray',
    config='build',
    tests=['testfiles/*.lvt'],
)

tblr_old = TestSuite(
    name='tabularray-old',
    alias='tblr-old',
    path='tabularray',
    config='config-old',
    tests=['testfiles-old/*.tex'],
)

L3BUILD_TESTSUITES: Final[tuple[TestSuite, ...]] = (zutil, tblr, tblr_old)
L3BUILD_TESTSUITES_MAP: Final[dict[str, TestSuite]] = {
    ts.alias: ts for ts in L3BUILD_TESTSUITES if ts.alias
} | {ts.name: ts for ts in L3BUILD_TESTSUITES}

L3BUILD_COMMANDS: Final[tuple[str, ...]] = ('check', 'save')


def on_ci() -> bool:
    """Check if the script is running on a CI environment."""
    # GitHub Actions sets 'CI'
    # https://docs.github.com/en/actions/reference/variables-reference#default-environment-variables
    return os.getenv('CI') == 'true'


def debug_logging_enabled() -> bool:
    """Check if debug logging is enabled."""
    # debug logging envvars
    # https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/troubleshooting-workflows/enabling-debug-logging
    return 'DEBUG' in os.environ or (
        on_ci()
        and (
            os.getenv('ACTIONS_RUNNER_DEBUG') == 'true'
            or os.getenv('ACTIONS_STEP_DEBUG') == 'true'
        )
    )


def wrap_l3build(args: argparse.Namespace) -> None:  # noqa: C901
    """Run l3build on each test suite."""
    target: str = args.target
    testsuites_run: dict[str, TestSuiteRun] = {
        ts.name: TestSuiteRun(ts) for ts in L3BUILD_TESTSUITES
    }

    # process names
    names: set[str] = set(args.names)
    known_names: list[str] = []
    for name in names:
        if name.startswith('-'):
            raise ValueError(f'Unknown option: "{name}".')  # noqa

        for ts in L3BUILD_TESTSUITES:
            ts_run = testsuites_run[ts.name]
            if name in (ts.name, ts.alias):
                # `name` is a testsuite name (or alias)
                known_names.append(name)
                ts_run.run_as_whole = True
            elif name in ts.get_names():
                # `name` is a test name
                known_names.append(name)
                ts_run.add_name(name)

    if set(known_names) != names:
        raise ValueError(f'Unknown name(s): {names - set(known_names)}.')  # noqa

    # compose and run l3build commands
    l3build_called: bool = False
    for ts_run in testsuites_run.values():
        if not ts_run.run_as_whole and not ts_run.names:
            continue
        l3build_called = True

        ts_run.finalize_names(args)
        ts_run.set_options(args)

        commands = ['l3build', target, *ts_run.options, *ts_run.names]
        if args.dry_run or args.verbose:
            print(f'[l3build.py] Running "{" ".join(commands)}" in directory "{ts_run.ts.path}"')  # noqa: E501 # fmt: skip
        if not args.dry_run:
            try:
                run(commands, cwd=ts_run.ts.path, check=True)  # noqa: S603
            except CalledProcessError:
                sys.exit(1)

    if not l3build_called:
        raise ValueError('No testsuites nor names passed.')  # noqa


parser = argparse.ArgumentParser(
    description='A l3build wrapper',
    usage='%(prog)s target [options] name...',
    epilog='Not all l3build options are supported.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
# fmt: off
parser.add_argument('target', type=str,
                    choices=L3BUILD_COMMANDS,
                    metavar='target',
                    help=f'the l3build target to run {L3BUILD_COMMANDS}')
parser.add_argument('names', type=str, nargs='*', metavar='name',
                    help='testsuite or test in one or more testsuites')
# inherited frequently-used l3build options
# Unlike in vanilla l3build.lua, options can be intermixed with names,
# and uses like `-qs` are accepted.
parser.add_argument('-e', '--engine', type=str)
parser.add_argument('-s', '--stdengine', action='store_true', default=False)
parser.add_argument('-S', '--show-saves', action='store_true', default=False)
# more l3build options
parser.add_argument('--dev', action='store_true', default=False)
parser.add_argument('--dirty', action='store_true', default=False)
parser.add_argument('-H', '--halt-on-error', action='store_true',
                    default=False)
parser.add_argument('--show-log-on-error', action='store_true',
                    default=False)
# modified options
parser.add_argument('-q', '--quiet',
                    action=argparse.BooleanOptionalAction,
                    default=True,
                    help='suppress TeX standard output (local patch added support for "save" target)')  # noqa: E501
# new options
parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                    help='print what l3build command(s) would be executed without execution')  # noqa: E501
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='print debug information (local patch needed)')
# fmt: on

if __name__ == '__main__':
    args = parser.parse_intermixed_args()

    if debug_logging_enabled():
        args.verbose = True

    if args.verbose:
        print(f'[l3build.py] Parsed args: {args}')

    wrap_l3build(args)
