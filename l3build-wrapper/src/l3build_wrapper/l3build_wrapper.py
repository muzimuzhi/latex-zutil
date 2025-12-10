#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

# Python 3.12 is needed by `if type not in Target`: check if a `EnumStr`
# class contains some value.
# https://docs.python.org/3/library/enum.html#enum.EnumType.__contains__
# Required python version is also recorded in `pyproject.toml`.

"""Check and save selective l3build tests made easier."""

import argparse
import fnmatch
import logging
import os
import subprocess
import sys
from dataclasses import asdict, dataclass, replace
from enum import UNIQUE, StrEnum, verify
from pathlib import Path
from typing import Final, NewType

Engines = NewType('Engines', tuple[str, ...])
Names = NewType('Names', set[str])
Options = NewType('Options', list[str])


# suggested by https://stackoverflow.com/a/60465422
class L3buildWrapperError(Exception):
    """Base class for L3buildWrapper exceptions."""


class InvalidTestSuiteError(L3buildWrapperError):
    """Invalid test suite was provided."""

    def __init__(self, value: str, reason: str, note: str = '') -> None:
        msg = f'{reason}: "{value}".' + ('' if note else f' {note}')
        super().__init__(msg)
        self.msg = msg


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
        super().__init__(
            f'Unknown name: "{name}". '
            'It matches neither a test suite nor a test in any test suites.'
        )
        self.name = name


@verify(UNIQUE)
class Target(StrEnum):
    """Enum for l3build targets."""

    CHECK = 'check'
    SAVE = 'save'


@dataclass
class _TestSuiteDefault:
    """Base class for l3build test suite defaults."""

    config: str
    checkengines: list[str]
    lvtext: str
    tlgext: str
    pvtext: str
    pdfext: str


@dataclass
class TestSuite(_TestSuiteDefault):
    """A l3build test suite."""

    name: str
    path: str = ''
    testfiledir: str = ''
    stdengine: str = ''
    alias: str | None = None
    test_names: Names | None = None
    test_results: Names | None = None

    def __post_init__(self) -> None:  # noqa: C901
        """More initialization with checks."""
        if not self.name:
            raise InvalidTestSuiteError(self.name, 'Missing test suite name')

        if not self.path:
            self.path = self.name

        base_dir = Path(self.path)
        if not base_dir.is_dir():
            raise InvalidTestSuiteError(str(base_dir), 'Directory not found')

        config_file = base_dir / (self.config + '.lua')
        if not config_file.is_file():
            raise InvalidTestSuiteError(
                str(config_file),
                'Configuration file not found',
            )

        # autoset testfiledir
        if not self.testfiledir:
            if self.config == 'build':
                self.testfiledir = 'testfiles'
            elif self.config.startswith('config-'):
                self.testfiledir = 'testfiles-' + self.config.removeprefix('config-')
        test_dir = base_dir / self.testfiledir
        if not test_dir.is_dir():
            raise InvalidTestSuiteError(str(test_dir), 'Directory not found')
        self.test_dir: Path = test_dir

        if not self.checkengines:
            raise InvalidTestSuiteError(str(self.checkengines), 'Empty checkengines')
        if not self.stdengine:
            self.stdengine = self.checkengines[0]

        for ext in (self.lvtext, self.tlgext, self.pvtext, self.pdfext):
            if not ext.startswith('.'):
                raise InvalidTestSuiteError(ext, 'Invalid file extension')

    def _glob_to_names(self, glob: str) -> Names:
        """Get set of names matching the given glob pattern."""
        # {i for i in iterable} is set comprehension
        return Names({p.stem for p in self.test_dir.glob(glob) if p.is_file()})

    def get_names(self) -> Names:
        """Generate test names from the test patterns."""
        if self.test_names is not None:
            return self.test_names

        names = Names(set())
        for ext in (self.lvtext, self.pvtext):
            _names = self._glob_to_names('*' + ext)
            if names & _names:
                logger.warning(
                    'Same name(s) exist in multiple test types: %s',
                    ', '.join(names & _names),
                )
            names |= _names

        if not names:
            logger.warning('No tests found for test suite "%s"', self.name)
        self.test_names = names
        return names

    def get_results(self) -> Names:
        """Get test results for this test suite."""
        if self.test_results is not None:
            return self.test_results

        names = Names(set())
        for ext in (self.tlgext, self.pdfext):
            names |= self._glob_to_names('*' + ext)

        if not names:
            logger.warning('No test results found for test suite "%s"', self.name)
        self.test_results = names
        return names


class TestSuiteRun:
    """Data needed by running l3build on a single test suite."""

    target: Target
    options_shared: Options

    def __init__(self, ts: TestSuite) -> None:
        self.name = ts.name
        self.ts = ts
        self.options: Options = Options([])
        self.names: Names = Names(set())
        self.run_as_whole: bool = False

    @classmethod
    def set_shared_target(cls, target: Target) -> None:
        """Set the target for all test suite runs."""
        cls.target = target

    @classmethod
    def set_shared_options(cls, args: argparse.Namespace) -> None:
        """Compose options for all test suite runs."""

        def add_option(option: str) -> None:
            _options.append(option)

        _options = Options([])
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
                    'Save all tests in test suite "%s"',
                    self.ts.name,
                )
                self.names = self.ts.get_names()
            # `check` a testsuite means checking with no explicit names
            elif self.target == Target.CHECK:
                self.names = Names(set())

    def set_options(self, args: argparse.Namespace) -> None:
        """Compose l3build options specific to this test suite."""

        def add_option(option: str) -> None:
            self.options.append(option)

        if self.ts.config:
            add_option(f'-c{self.ts.config}')
        if args.engine and args.engine not in (self.ts.stdengine, _OPTION_ALL_ENGINES):
            add_option(f'-e{args.engine}')

    def parse_known_names(
        self,
        names: Names,
    ) -> Names:
        """Parse names received from the command line."""
        ts = self.ts
        names_unknown = Names(set())
        for name in names:
            # a name is either a test suite or a test glob, but not both
            if name in (ts.name, ts.alias):
                self.run_as_whole = True
                logger.debug(
                    'Name "%s" recognized as a test suite "%s"',
                    name, ts.name,
                )  # fmt: skip
            elif _glob_names := fnmatch.filter(ts.get_names(), name):
                self.names.update(_glob_names)
                logger.debug(
                    'Name glob "%s" recognized as test(s) in test suite "%s"',
                    name, ts.name,
                )  # fmt: skip
            else:
                names_unknown.add(name)
        return names_unknown

    def get_engine_specific_results(self, name: str) -> Engines:
        """Get list of engines from engine-specific test results."""
        ts = self.ts
        # if "name.tlg" and "name.pdf" both exist, but different sets of
        # engine-specific results exist, `l3build save -e... name` would
        # create new and unneeded test results.
        # TODO: check the behavior of l3build
        rst = [e for e in ts.checkengines if f'{name}.{e}' in ts.get_results()]
        return Engines(tuple(rst))

    def _invoke_l3build(
        self,
        target: Target,
        options: Options,
        names: Names,
        dry_run: bool,  # noqa: FBT001
    ) -> None:
        """Invoke l3build."""
        path = self.ts.path
        commands = ['l3build', target, *options, *sorted(names)]
        logger.info('Run "%s" in directory "%s"', ' '.join(commands), path)
        if dry_run:
            return
        try:
            subprocess.run(commands, cwd=path, check=True)  # noqa: S603
        except subprocess.CalledProcessError:
            logger.error('Failed to run l3build')
            sys.exit(1)

    def invoke_l3build(self, args: argparse.Namespace) -> bool:
        """Run l3build on this test suite."""

        def save_for_all_engines() -> None:
            name_groups: dict[Engines, Names] = {}
            for name in self.names:
                engines: Engines = self.get_engine_specific_results(name)
                if engines in name_groups:
                    name_groups[engines].add(name)
                else:
                    name_groups[engines] = Names({name})

            for engines, names in name_groups.items():
                if not engines:
                    # save for stdengine only
                    logger.info('Save test(s) "%s" in stdengine', ', '.join(names))
                    options = self.options
                else:
                    # save for stdengine and extra engines
                    _engines = Engines((self.ts.stdengine, *engines))
                    logger.info(
                        'Save test(s) "%s" in engines "%s"',
                        ', '.join(names),
                        ', '.join(_engines),
                    )
                    options = Options(
                        [op for op in self.options if not op.startswith('-e')]
                    )
                    options.append(f'-e{",".join(_engines)}')
                self._invoke_l3build(self.target, options, names, args.dry_run)

        if not self.run_as_whole and not self.names:
            return False

        self.finalize_names()
        self.set_options(args)
        self.options.extend(TestSuiteRun.options_shared)

        if self.target == Target.SAVE and args.engine == _OPTION_ALL_ENGINES:
            save_for_all_engines()
        else:
            # simple case, run l3build on the test suite
            self._invoke_l3build(self.target, self.options, self.names, args.dry_run)

        if self.target == Target.SAVE and args.re_check:
            l3build_print('Re-checking tests', newline=True)
            # always set `-S, --show-saves` when re-checking
            if '-S' not in self.options:
                self.options.append('-S')
            self._invoke_l3build(Target.CHECK, self.options, self.names, args.dry_run)
        return True


LOGGING_DEFAULT_FORMAT = '[%(name)s] %(levelname)s: %(message)s'
LOGGING_DEBUG_FORMAT = '[%(name)s] %(levelname)-5s - %(filename)s:%(lineno)d - %(funcName)-17s - %(message)s'  # noqa: E501

LOGGER_NAME: Final[str] = 'wrapper'

_OPTION_ALL_ENGINES: Final[str] = '_option_all_engines'

TESTSUITE_DEFAULT: Final = _TestSuiteDefault(
    config='build',
    checkengines=['pdftex', 'luatex', 'xetex'],
    lvtext='.lvt',
    tlgext='.tlg',
    pvtext='.pvt',
    pdfext='.pdf',
)
_DEFAULT: Final = asdict(TESTSUITE_DEFAULT)

zutil: Final[TestSuite] = TestSuite(
    **_DEFAULT,
    name='zutil',
)
tblr: Final[TestSuite] = TestSuite(
    **_DEFAULT,
    name='tabularray',
    alias='tblr',
)
tblr_old: Final[TestSuite] = replace(
    tblr,
    name='tabularray-old',
    alias='tblr-old',
    config='config-old',
    testfiledir='testfiles-old',
    lvtext='.tex',
)

L3BUILD_TESTSUITES: Final[tuple[TestSuite, ...]] = (
    zutil,
    tblr,
    tblr_old,
)
L3BUILD_TESTSUITES_MAP: Final[dict[str, TestSuite]] = {
    ts.alias: ts for ts in L3BUILD_TESTSUITES if ts.alias
} | {ts.name: ts for ts in L3BUILD_TESTSUITES}

VERBOSITY_TO_LEVEL: Final[dict[int, int]] = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}

# init logger
logging.basicConfig(format=LOGGING_DEFAULT_FORMAT)
logger = logging.getLogger(LOGGER_NAME)


def l3build_print(*args: str, newline: bool = False) -> None:
    """Print ordinary output prefixed with logger name.

    See https://docs.python.org/3/howto/logging.html#when-to-use-logging.
    """
    print(f'{'\n' if newline else ''}[{LOGGER_NAME}]', *args)


def l3build_patched() -> bool:
    """Check if the l3build is patched (aka, run locally)."""
    try:
        rst = subprocess.run(['l3build', '--version'], check=True, capture_output=True)  # noqa: S607
        return '(with patch)' in rst.stdout.decode('utf-8')
    except subprocess.CalledProcessError:
        logger.exception('"l3build --version" failed.')

    return False


def debug_logging_enabled() -> bool:
    """Check if debug logging is enabled by environment variables."""

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

    return 'DEBUG' in os.environ or (on_ci() and github_debug_logging_enabled())


def set_logging(args: argparse.Namespace) -> None:
    """Update logging settings."""

    def set_level(level: int) -> None:
        if level == logging.DEBUG:
            logging.basicConfig(format=LOGGING_DEBUG_FORMAT)
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
        names = Names(set(args.names))
        unknown = names.copy()
        for ts_run in testsuites_run.values():
            unknown = unknown.intersection(ts_run.parse_known_names(names))
        if unknown:
            raise UnknownNameError(unknown.pop())

    # invoke l3build
    invoked = False
    for ts_run in testsuites_run.values():
        invoked |= ts_run.invoke_l3build(args)
    if not invoked:
        # should not happen, but just in case
        logger.warning('No l3build commands were invoked.')


# Unlike in vanilla l3build,
# - options can be intermixed with names,
# - quite some options are made flags, i.e., they don't take arguments,
# - short flags are mergeable (`-qs` is the same as `-q -s`).
parser = argparse.ArgumentParser(
    description='Check and save selective l3build tests made easier',
    usage='%(prog)s target [options] name...',
    epilog='Not all l3build options are supported.',
    exit_on_error=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
# fmt: off
# positional arguments
parser.add_argument('target', type=str,
                    help=f'a l3build target to run {[t.value for t in Target]}')
parser.add_argument('names', type=str, nargs='*', metavar='name',
                    help='a name of test suite or a glob for test name(s)')

# new, wrapper-only options and flags
# `--all-engines` and `-e/--engine` overwrite each other so the last one wins
parser.add_argument('--all-engines',
                    dest='engine',
                    action='store_const',
                    const=_OPTION_ALL_ENGINES,
                    help='run on all existing test results; '
                         'useful for auto-saving engine-specific tests')
parser.add_argument('-n', '--dry-run', action='store_true',
                    help='print what l3build command(s) would be executed without execution')  # noqa: E501
parser.add_argument('--re-check', '--recheck',
                    action='store_true',
                    help='after saving, rerun checks using the same arguments')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='print more information; given twice enables debug logging and would be passed to "l3build" if patched l3build is detected')  # noqa: E501

# inherited l3build options and flags
inherited = parser.add_argument_group('inherited l3build options')
inherited.add_argument('--dev', action='store_true')
inherited.add_argument('--dirty', action='store_true')
inherited.add_argument('-e', '--engine', type=str)
inherited.add_argument('-H', '--halt-on-error', action='store_true')
inherited.add_argument('-q', '--quiet',
                       action=argparse.BooleanOptionalAction,
                       default=True,
                       help='suppress TeX standard output (support for "save" target needs local l3build patch)')  # noqa: E501
inherited.add_argument('--show-log-on-error', action='store_true')
inherited.add_argument('-S', '--show-saves', action='store_true')
inherited.add_argument('-s', '--stdengine', action='store_true')
# fmt: on


def main(argv: list[str] | None = None) -> None:
    """Main function to run the l3build wrapper."""  # noqa: D401
    try:
        # `args` defaults to `None`, which is equivalent to passing `sys.argv[1:]`
        args = parser.parse_intermixed_args(args=argv)

        set_logging(args)
        wrap_l3build(args)
    except KeyboardInterrupt:
        logger.warning('Interrupted by user')
        sys.exit(1)
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


if __name__ == '__main__':
    main()
