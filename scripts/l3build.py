#!/usr/bin/env -S uv run --script

from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Final

import argparse
import os
import sys


class TestSuite:
    def __init__(self, name: str, path: str, config: str, tests: list[str], alias: str | None = None) -> None:
        self.name = name
        self.alias = alias
        self.path = path
        self.config = config
        self.tests = tests
        self.test_names: tuple[str] | None = None

    def resolve_tests(self) -> tuple[str, ...]:
        """Resolve the test patterns to actual test names."""
        if self.test_names is not None:
            return self.test_names

        test_names = []
        for test in self.tests:
            test_names.extend([p.stem for p in Path(self.path).glob(test)])
        self.test_names = tuple(test_names)
        return self.test_names


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
L3BUILD_TESTSUITE_ALIASES: Final[dict[str, str]] = \
    { ts.alias: ts.name for ts in L3BUILD_TESTSUITES if ts.alias}

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
    target = args.target
    testsuite = None
    options = []
    names = []

    # compose testsuite and l3build names
    for name in args.names:
        if name.startswith('-'):
            raise ValueError(f"Unknown argument: {name}")
        name_raw = name
        name : str = L3BUILD_TESTSUITE_ALIASES.get(name, name)
        for ts in L3BUILD_TESTSUITES:
            if name == ts.name:
                if testsuite is None:
                    testsuite = ts
                elif testsuite != ts:
                    raise ValueError(
                        f"Multiple testsuites: testsuite {name_raw} "
                        f"doesn't contain tests {names}"
                    )
                else:
                    names = []
                break
            if name in ts.resolve_tests():
                if testsuite is None:
                    testsuite = ts
                elif testsuite != ts:
                    raise ValueError(
                        f"Multiple testsuites: test {name} "
                        f"is not in testsuite {testsuite.name}"
                    )
                if name not in names:
                    names.append(name)
                break
        else:
            raise ValueError(f"Unknown test name: {name}")

    if testsuite is None:
        raise ValueError("No testsuites nor names passed.")

    # compose l3build options
    if testsuite.config:
        options.append(f'-c{testsuite.config}')
    if args.engine:
        options.append(f'-e{args.engine}')
    if args.stdengine:
        options.append('-s')
    if args.quiet:
        options.append('-q')
    if args.verbose and not on_ci():
        options.append('-v')
    if args.halt_on_error:
        options.append('-H')
    if args.dev:
        options.append('--dev')
    if args.dirty:
        options.append('--dirty')
    if args.show_log_on_error:
        options.append('--show-log-on-error')

    # 'save' target without names means saving all
    if target == 'save' and not names:
        names = testsuite.resolve_tests()

    if target == 'check' and args.show_saves:
        options.append('-S')

    commands = ['l3build', target, *options, *names]
    if args.dry_run or args.verbose:
        print(f"[l3build.py] Running '{' '.join(commands)}' in directory '{testsuite.path}'")
    if not args.dry_run:
        try:
            run(commands, cwd=testsuite.path, check=True)
        except CalledProcessError:
            sys.exit(1)


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
                    help='testsuite or test')
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
