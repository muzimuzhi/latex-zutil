#!/usr/bin/env -S uv run --script

import argparse
from pathlib import Path
from subprocess import run

import test


class TestSuite:
    def __init__(self, path: str, config: str, tests: tuple[str]) -> None:
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
    path = 'zutil',
    config = 'build',
    tests = ('testfiles/zutil-*.lvt',)
)

tblr = TestSuite(
    path = 'tabularray',
    config = 'build',
    tests = ('testfiles/tblr-*.lvt',)
)

tblr_old = TestSuite(
    path = 'tabularray',
    config = 'config-old',
    tests = ('testfiles-old/*.tex',)
)

L3BUILD_COMMANDS = ('check', 'save')
L3BUILD_TESTSUITES = {
    'zutil': zutil,
    'tabularray': tblr,
    'tabularray-old': tblr_old,
}
L3BUILD_TESTSUITE_ALIASES = {
    'tblr': 'tabularray',
    'tblr-old': 'tabularray-old',
}


def resolve_name_alias(name: str) -> str:
    return L3BUILD_TESTSUITE_ALIASES.get(name, name)


def parse_args(args: argparse.Namespace, unknown_args: list[str]) -> None:
    """Parse command line arguments."""
    target = args.target
    testsuite = None
    options = []
    names = []

    # parse unknown arguments
    for name in unknown_args:
        name = resolve_name_alias(name)
        if name.startswith('-'):
            raise ValueError(f"Unknown argument: {name}")
        elif name in L3BUILD_TESTSUITES:
            testsuite = L3BUILD_TESTSUITES[name]
        else:
            for ts in L3BUILD_TESTSUITES.values():
                if name in ts.resolve_tests():
                    if testsuite is None:
                        testsuite = ts
                    elif testsuite != ts:
                        raise ValueError(f"Multiple testsuites: test {name} is not in testsuite {testsuite.path}")
                    if name not in names:
                        names.append(name)
                    break
            else:
                raise ValueError(f"Unknown test name: {name}")

    # generate l3build options
    if args.engine:
        options.append(f'-e{args.engine}')
    if args.stdengine:
        options.append('-s')
    if args.quiet:
        options.append('-q')

    if testsuite is None:
        raise ValueError("No testsuite recognized.")

    if testsuite.config != 'build':
        options.append(f'-c{testsuite.config}')

    if target == 'save' and not names:
        names = testsuite.resolve_tests()

    print(f"cd {testsuite.path}")
    run(['echo', 'l3build', target, *options, *names], cwd=testsuite.path)

parser = argparse.ArgumentParser(
    description='A l3build wrapper',
    allow_abbrev=False,
)
parser.add_argument('target', type=str, choices=L3BUILD_COMMANDS, help='The l3build target to run')
parser.add_argument('-e', '--engine', type=str)
parser.add_argument('-s', '--stdengine', action='store_true', default=False)
parser.add_argument('-q', '--quiet', action='store_true', default=True)


if __name__ == "__main__":
    args, unknown_args = parser.parse_known_intermixed_args()
    parse_args(args, unknown_args)
