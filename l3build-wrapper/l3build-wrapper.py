#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# Python 3.12 is needed by the `type` alias statement.
# Required python version is also recorded in `ruff.toml`.

"""Check and save selective l3build tests made easier."""

import argparse
import logging
import os
import sys
from enum import UNIQUE, StrEnum, verify
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import Final

type Test = str


logger = logging.getLogger('wrapper')


# suggested by https://stackoverflow.com/a/60465422
class L3buildWrapperError(Exception):
    """Base class for L3buildWrapper exceptions."""


class UnknownTargetError(L3buildWrapperError):
    """Unknown target was provided."""

    def __init__(self, target: str) -> None:
        super().__init__(f'Unknown target: "{target}".')
        self.target = target


# https://docs.astral.sh/ruff/rules/raise-vanilla-args/
class NameRequiredError(L3buildWrapperError):
    """No names were provided."""

    def __init__(self, target: str) -> None:
        super().__init__(f'Target "{target}" needs at least one name.')
        self.target = target


class UnknownNameError(L3buildWrapperError):
    """Unknown name was provided."""

    def __init__(self, name: str) -> None:
        super().__init__(f'Unknown name: "{name}".')
        self.name = name


@verify(UNIQUE)
class Target(StrEnum):
    """Enum for l3build targets."""

    CHECK = 'check'
    SAVE = 'save'


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

    target: Target
    options_shared: list[str]

    def __init__(self, ts: TestSuite) -> None:
        self.name = ts.name
        self.ts = ts
        self.options: list[str] = []
        self.names: list[Test] = []
        self.run_as_whole: bool = False

    @classmethod
    def set_shared_target(cls, target: Target) -> None:
        """Set the target for all test suite runs."""
        cls.target = target

    @classmethod
    def set_shared_options(cls, args: argparse.Namespace) -> None:
        """Set options for all test suite runs."""

        def add_option(option: str) -> None:
            _options.append(option)

        _options = []
        if args.stdengine:
            add_option('-s')
        if args.quiet:
            add_option('-q')
        if logger.getEffectiveLevel() == logging.DEBUG and l3build_patched():
            add_option('-v')
        if args.halt_on_error:
            add_option('-H')
        if cls.target == Target.CHECK and args.show_saves:
            add_option('-S')
        if args.dev:
            add_option('--dev')
        if args.dirty:
            add_option('--dirty')
        if args.show_log_on_error:
            add_option('--show-log-on-error')
        cls.options_shared = _options

    def finalize_names(self) -> None:
        """Adjust collected test names at final stage."""
        if self.run_as_whole:
            # `save` a testsuite means saving all names in it
            if self.target == Target.SAVE:
                logger.info(
                    'Saving all tests in test suite "%s"',
                    self.ts.name,
                )
                self.names = list(self.ts.get_names())
            # `check` a testsuite means checking with no names
            elif self.target == Target.CHECK:
                self.names = []

    def set_options(self, args: argparse.Namespace) -> None:
        """Compose l3build options."""

        def add_option(option: str) -> None:
            self.options.append(option)

        if self.ts.config:
            add_option(f'-c{self.ts.config}')
        if args.engine:
            add_option(f'-e{args.engine}')

    def parse_known_names(
        self,
        names: set[str],
    ) -> list[str]:
        """Parse names received from the command line."""

        def add_name(name: Test) -> None:
            """Add a test name."""
            if name not in self.names:
                self.names.append(name)

        ts = self.ts
        names_unknown = []
        for name in names:
            if name in (ts.name, ts.alias):
                self.run_as_whole = True
                logger.debug(
                    'Name "%s" recognized as a test suite "%s"',
                    name, ts.name,
                )  # fmt: skip
            elif name in ts.get_names():
                add_name(name)
                logger.debug(
                    'Name "%s" recognized as a test in test suite "%s"',
                    name, ts.name,
                )  # fmt: skip
            else:
                names_unknown.append(name)
        return names_unknown

    def invoke_l3build(self, args: argparse.Namespace) -> bool:
        """Run l3build on this test suite."""
        if not self.run_as_whole and not self.names:
            return False

        self.finalize_names()
        self.set_options(args)
        self.options.extend(TestSuiteRun.options_shared)

        commands = ['l3build', self.target, *self.options, *self.names]
        path = self.ts.path
        logger.info('Running "%s" in directory "%s"', ' '.join(commands), path)
        if not args.dry_run:
            try:
                run(commands, cwd=path, check=True)  # noqa: S603
            except CalledProcessError:
                sys.exit(1)
        return True


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

LOGGING_DEFAULT_FORMAT = '[%(name)s] %(levelname)s: %(message)s'
LOGGING_DEBUG_FORMAT = '[%(name)s] %(levelname)-5s - %(filename)s:%(lineno)d - %(funcName)-17s - %(message)s'  # noqa: E501

L3BUILD_TESTSUITES: Final[tuple[TestSuite, ...]] = (zutil, tblr, tblr_old)
L3BUILD_TESTSUITES_MAP: Final[dict[str, TestSuite]] = {
    ts.alias: ts for ts in L3BUILD_TESTSUITES if ts.alias
} | {ts.name: ts for ts in L3BUILD_TESTSUITES}

VERBOSITY_TO_LEVEL: Final[dict[int, int]] = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def l3build_patched() -> bool:
    """Check if the l3build is patched (aka, run locally)."""
    try:
        rst = run(['l3build', '--version'], check=True, capture_output=True)  # noqa: S607
    except CalledProcessError:
        logger.exception('"l3build --version" failed.')

    return '(with patch)' in rst.stdout.decode('utf-8')


def on_ci() -> bool:
    """Check if the script is running on a CI environment."""
    # GitHub Actions sets 'CI'
    # https://docs.github.com/en/actions/reference/variables-reference#default-environment-variables
    return os.getenv('CI') == 'true'


def github_debug_logging_enabled() -> bool:
    """Check if GitHub Actions debug logging is enabled."""
    # https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/troubleshooting-workflows/enabling-debug-logging
    return (
        os.getenv('ACTIONS_RUNNER_DEBUG') == 'true'
        or os.getenv('ACTIONS_STEP_DEBUG') == 'true'
    )


def debug_logging_enabled() -> bool:
    """Check if debug logging is enabled by environment variables."""
    return 'DEBUG' in os.environ or (on_ci() and github_debug_logging_enabled())


def set_logging_level(args: argparse.Namespace) -> None:
    """Set logging level."""

    def set_level(level: int) -> None:
        if level == logging.DEBUG:
            logging.basicConfig(format=LOGGING_DEBUG_FORMAT)
        else:
            logging.basicConfig(format=LOGGING_DEFAULT_FORMAT)
        logger.setLevel(level)
        logger.debug('Logging level set to %s', logging.getLevelName(level))

    level = VERBOSITY_TO_LEVEL.get(args.verbose, logging.DEBUG)
    if debug_logging_enabled():
        level = min(level, logging.DEBUG)
    elif args.dry_run:
        level = min(level, logging.INFO)

    set_level(level)


def wrap_l3build(args: argparse.Namespace) -> None:
    """Run l3build on one test suite a time."""
    logger.debug('Parsed args: %s', args)

    target = args.target
    if target not in Target:
        raise UnknownTargetError(target)

    TestSuiteRun.set_shared_target(Target(target))
    logger.debug('Shared target: "%s"', target)
    TestSuiteRun.set_shared_options(args)
    logger.debug('Shared options: %s', TestSuiteRun.options_shared)

    testsuites_run: dict[str, TestSuiteRun] = {
        ts.name: TestSuiteRun(ts) for ts in L3BUILD_TESTSUITES
    }

    if not args.names:
        if target == Target.SAVE:
            raise NameRequiredError(target)
        logger.info('Checking all test suites')
        for ts_run in testsuites_run.values():
            ts_run.run_as_whole = True
    else:
        # parse names
        names = set(args.names)
        unknown = names.copy()
        for ts_run in testsuites_run.values():
            unknown = unknown.intersection(ts_run.parse_known_names(names))
        if unknown:
            raise UnknownNameError(unknown.pop())

    # run l3build
    invoked = False
    for ts_run in testsuites_run.values():
        invoked |= ts_run.invoke_l3build(args)
    if not invoked:
        # should not happen, but just in case
        logger.warning('No l3build commands were invoked.')


# Unlike in vanilla l3build, options can be intermixed with names,
# and short flags are mergeable (`-qs` is the same as `-q -s`).
parser = argparse.ArgumentParser(
    description='Check and save selective l3build tests made easier',
    usage='%(prog)s target [options] name...',
    epilog='Not all l3build options are supported.',
    exit_on_error=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
# fmt: off
parser.add_argument('target', type=str,
                    help=f'the l3build target to run {[t.value for t in Target]}')
parser.add_argument('names', type=str, nargs='*', metavar='name',
                    help='a test suite or test')

# new, wrapper-only options
parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                    help='print what l3build command(s) would be executed without execution')  # noqa: E501
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='print more information; given twice enables debug logging and would be passed to "l3build" if patched l3build is detected)')  # noqa: E501

_inherited = parser.add_argument_group('inherited l3build options')
# commonly used l3build options
_inherited.add_argument('-e', '--engine', type=str)
_inherited.add_argument('-s', '--stdengine', action='store_true',
                        default=False)
_inherited.add_argument('-S', '--show-saves', action='store_true',
                        default=False)
# more l3build options
_inherited.add_argument('--dev', action='store_true', default=False)
_inherited.add_argument('--dirty', action='store_true', default=False)
_inherited.add_argument('-H', '--halt-on-error', action='store_true',
                        default=False)
_inherited.add_argument('--show-log-on-error', action='store_true',
                        default=False)

_improved = parser.add_argument_group('enhanced l3build options')
# modified options
_improved.add_argument('-q', '--quiet',
                       action=argparse.BooleanOptionalAction,
                       default=True,
                       help='suppress TeX standard output (support for "save" target needs local l3build patch)')  # noqa: E501
# fmt: on

if __name__ == '__main__':
    try:
        args = parser.parse_intermixed_args()
        set_logging_level(args)
        wrap_l3build(args)
    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        logger.error(str(e))
        parser.print_usage()
        sys.exit(2)
    except NameRequiredError as e:
        logger.error(e)
        parser.print_usage()
        sys.exit(2)
    except L3buildWrapperError as e:
        # TODO: logger.exception() logs exception info without color
        logger.error(e)
        sys.exit(1)
    except Exception:
        logger.exception('Unexpected error')
