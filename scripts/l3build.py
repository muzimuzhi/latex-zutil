#!/usr/bin/env -S uv run --script

from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Final

import argparse
import os
import sys


type Test = str

class TestSuite:
    def __init__(self, name: str, path: str, config: str, tests: list[Test], alias: str | None = None) -> None:
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


class RunNames:
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

    def add_option(self, option: str) -> None:
        """Set the options for the test suite run."""
        self.options.append(option)

    def finalize_names(self, args: argparse.Namespace) -> None:
        if self.run_as_whole:
            # `save` a testsuite means saving all names in it
            if args.target == 'save':
                self.names = list(self.ts.get_names())
            # `check` a testsuite means checking with no names
            elif args.target == 'check':
                self.names = []

    def set_options(self, args: argparse.Namespace) -> None:
        if self.ts.config:
            self.add_option(f'-c{self.ts.config}')
        if args.engine:
            self.add_option(f'-e{args.engine}')
        if args.stdengine:
            self.add_option('-s')
        if args.quiet:
            self.add_option('-q')
        if args.verbose and not on_ci():
            self.add_option('-v')
        if args.halt_on_error:
            self.add_option('-H')
        if args.target == 'check' and args.show_saves:
            self.add_option('-S')
        if args.dev:
            self.add_option('--dev')
        if args.dirty:
            self.add_option('--dirty')
        if args.show_log_on_error:
            self.add_option('--show-log-on-error')


zutil = TestSuite(
    name = 'zutil',
    path = 'zutil',
    config = 'build',
    tests = ['testfiles/*.lvt']
)

tblr = TestSuite(
    name = 'tabularray',
    alias = 'tblr',
    path = 'tabularray',
    config = 'build',
    tests = ['testfiles/*.lvt']
)

tblr_old = TestSuite(
    name = 'tabularray-old',
    alias = 'tblr-old',
    path = 'tabularray',
    config = 'config-old',
    tests = ['testfiles-old/*.tex']
)

L3BUILD_TESTSUITES: Final[tuple[TestSuite, ...]] = \
    (zutil, tblr, tblr_old)
L3BUILD_TESTSUITES_MAP: Final[dict[str, TestSuite]] = \
    { ts.alias: ts for ts in L3BUILD_TESTSUITES if ts.alias } | \
    { ts.name: ts for ts in L3BUILD_TESTSUITES }

L3BUILD_COMMANDS: Final[tuple[str, ...]] = \
    ('check', 'save')


def on_ci() -> bool:
    """Check if the script is running on a CI environment."""
    # GitHub Actions sets 'CI'
    # https://docs.github.com/en/actions/reference/variables-reference#default-environment-variables
    return os.getenv('CI') == 'true'

def debug_logging_enabled() -> bool:
    """Check if debug logging is enabled."""
    # debug logging envvars
    # https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/troubleshooting-workflows/enabling-debug-logging
    return 'DEBUG' in os.environ or \
        (on_ci() and\
            (os.getenv('ACTIONS_RUNNER_DEBUG') == 'true' or\
            os.getenv('ACTIONS_STEP_DEBUG') == 'true'))


def parse_args(args: argparse.Namespace) -> None:
    """Parse command line arguments."""
    target: str = args.target
    testsuites_run: dict[str, RunNames] = \
        { ts.name: RunNames(ts) for ts in L3BUILD_TESTSUITES }

    # process names
    names = set(args.names)
    known_names: list[str] = []
    for name in names:
        if name.startswith('-'):
            raise ValueError(f"Unknown option: \"{name}\".")

        for ts in L3BUILD_TESTSUITES:
            ts_run = testsuites_run[ts.name]
            if name == ts.name or name == ts.alias:
                # `name` is a testsuite name (or alias)
                known_names.append(name)
                ts_run.run_as_whole = True
            elif name in ts.get_names():
                # `name` is a test name
                known_names.append(name)
                ts_run.add_name(name)

    if set(known_names) != names:
        raise ValueError(f"Unknown name(s): {names - set(known_names)}.")

    # import pprint
    # for ts_run in testsuites_run.values():
    #     pprint.pprint(ts_run.__dict__)
    # os._exit(0)  # for debugging

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
            print(f"[l3build.py] Running '{' '.join(commands)}' in directory '{ts_run.ts.path}'")
        if not args.dry_run:
            try:
                run(commands, cwd=ts_run.ts.path, check=True)
            except CalledProcessError:
                sys.exit(1)

    if not l3build_called:
        raise ValueError("No testsuites nor names passed.")


parser = argparse.ArgumentParser(
    description='A l3build wrapper',
    usage='%(prog)s target [options] name...',
    # allow_abbrev=False, # isn't --no-q more useful than --no-quiet?
    epilog='Not all l3build options are supported.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
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
                    help='suppress output (local patch added support for "save" target)')
# new options
parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                    help='print what l3build command(s) would be executed without execution')
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    help='print debug information (local patch needed)')

if __name__ == "__main__":
    args = parser.parse_intermixed_args()

    if debug_logging_enabled():
        args.verbose = True

    if args.verbose:
        print(f"[l3build.py] Parsed args: {args}")

    parse_args(args)
