#!/usr/bin/env -S uv run --script

from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from pathlib import Path
from subprocess import run
from typing import Final


class TestSuite:
    def __init__(self, name: str, directory: str, config: str, tests: tuple[str], alias: str = "") -> None:
        self.name = name
        self.alias = alias
        self.directory = directory
        self.config = config
        self.tests = tests
        self.test_names: tuple[str] | None = None

    def resolve_tests(self) -> tuple[str, ...]:
        """Resolve the test patterns to actual test names."""
        if self.test_names is not None:
            return self.test_names

        test_names = []
        for test in self.tests:
            test_names.extend([p.stem for p in Path(self.directory).glob(test)])
        self.test_names = tuple(test_names)
        return self.test_names


zutil = TestSuite(
    name = 'zutil',
    directory = 'zutil',
    config = 'build',
    tests = ('testfiles/*.lvt',)
)

tblr = TestSuite(
    name = 'tabularray',
    alias = 'tblr',
    directory = 'tabularray',
    config = 'build',
    tests = ('testfiles/*.lvt',)
)

tblr_old = TestSuite(
    name = 'tabularray-old',
    alias = 'tblr-old',
    directory = 'tabularray',
    config = 'config-old',
    tests = ('testfiles-old/*.tex',)
)

testsuites = (zutil, tblr, tblr_old)

L3BUILD_TESTSUITES: Final[dict[str, TestSuite]] = \
    { ts.name: ts for ts in testsuites }
L3BUILD_TESTSUITE_ALIASES: Final[dict[str, str]] = \
    { ts.alias: ts.name for ts in L3BUILD_TESTSUITES.values() if ts.alias}

L3BUILD_COMMANDS: Final[tuple[str, ...]] = \
    ('check', 'save')


def parse_args(args: Namespace) -> None:
    """Parse command line arguments."""
    target = args.target
    testsuite = None
    options = []
    names = []

    # compose testsuite and l3build names
    for name in args.names:
        name_raw = name
        name : str = L3BUILD_TESTSUITE_ALIASES.get(name, name)
        if name.startswith('-'):
            raise ValueError(f"Unknown argument: {name}")
        else:
            for ts in L3BUILD_TESTSUITES.values():
                if name == ts.name:
                    if testsuite is None:
                        testsuite = ts
                    elif testsuite != ts:
                        raise ValueError(
                            f"Multiple testsuites: testsuite {name_raw}"
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
                            f"Multiple testsuites: test {name}"
                            f"is not in testsuite {testsuite.name}"
                        )
                    if name not in names:
                        names.append(name)
                    break
            else:
                raise ValueError(f"Unknown test name: {name}")

    if testsuite is None:
        raise ValueError("No testsuite nor names passed.")

    # compose l3build options
    if args.engine:
        options.append(f'-e{args.engine}')
    if args.stdengine:
        options.append('-s')
    if args.quiet:
        options.append('-q')
    if args.dev:
        options.append('--dev')
    if args.halt_on_error:
        options.append('-H')
    if args.show_log_on_error:
        options.append('--show-log-on-error')
    if testsuite.config:
        options.append(f'-c{testsuite.config}')

    # 'save' target without names means saving all
    if target == 'save' and not names:
        names = testsuite.resolve_tests()

    if target == 'check' and args.show_saves:
        options.append('-S')

    commands = ['l3build', target, *options, *names]
    if args.dry_run:
        print(f"[l3build.py] Running '{' '.join(commands)}' in directory '{testsuite.directory}'")
    else:
        run(commands, cwd=testsuite.directory)


parser = ArgumentParser(
    description='A l3build wrapper',
    usage='%(prog)s target [options] name...',
    # allow_abbrev=False, # isn't --no-q more useful than --no-quiet?
    epilog='Not all l3build options are supported.'
)
parser.add_argument('target', type=str,
                    choices=L3BUILD_COMMANDS,
                    metavar='target',
                    help=f'the l3build target to run {L3BUILD_COMMANDS}')
parser.add_argument('names', type=str, nargs='*', metavar='name',
                    help='a testsuite or test')
# inherited frequently-used l3build options
# Unlike in vanilla l3build.lua, options can be intermixed with names,
# and uses like `-qs` are accepted.
parser.add_argument('-e', '--engine', type=str)
parser.add_argument('-s', '--stdengine', action='store_true', default=False)
parser.add_argument('-S', '--show-saves', action='store_true', default=False)
parser.add_argument('-q', '--quiet', action=BooleanOptionalAction,
                    default=True)
# more l3build options, mostly used on CI
parser.add_argument('--dev', action='store_true', default=False)
parser.add_argument('-H', '--halt-on-error', action='store_true',
                    default=False)
parser.add_argument('--show-log-on-error', action='store_true',
                    default=False)
# new options
parser.add_argument('-n', '--dry-run', action='store_true', default=False)


if __name__ == "__main__":
    args = parser.parse_intermixed_args()

    import os
    if 'DEBUG' in os.environ:
        print(f"[l3build.py] Parsed args: {args}")

    parse_args(args)
