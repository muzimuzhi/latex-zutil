#!/usr/bin/env -S uv run --script

import argparse
from dataclasses import dataclass
from pathlib import Path

from pprint import pprint

import test


class TestSuite:
    def __init__(self, path: str, config: str, tests: tuple[str]) -> None:
        self.path = path
        self.config = config
        self.tests = tests

    def resolve_tests(self) -> tuple[str, ...]:
        """Resolve the test patterns to actual file paths."""
        test_names = []
        for test in self.tests:
            test_names.extend([p.stem for p in Path(self.path).glob(test)])
        return tuple(test_names)

zutil = TestSuite(
    path = 'zutil',
    config = 'build.lua',
    tests = ('testfiles/zutil-*.lvt',)
)

tblr = TestSuite(
    path = 'tabularray',
    config = 'build.lua',
    tests = ('testfiles/tblr-*.lvt',)
)

tblr_old = TestSuite(
    path = 'tabularray',
    config = 'config-old.lua',
    tests = ('testfiles-old/*.tex',)
)

L3BUILD_COMMANDS = ('check', 'save')
# L3BUILD_TESTSUITES = (zutil, tblr, tblr_old)
L3BUILD_TESTSUITES = {
    'zutil': zutil,
    'tblr': tblr,
    'tabularray': tblr,
    'tblr-old': tblr_old,
    'tabularray-old': tblr_old,
}

def parse_args(args: argparse.Namespace, unknown_args: list[str]) -> None:
    """Parse command line arguments."""
    target = args.target
    testsuite = None
    options = []
    names = []

    # parse unknown arguments
    for name in unknown_args:
        if name.startswith('-'):
            raise ValueError(f"Unknown argument: {name}")
        elif name in L3BUILD_TESTSUITES:
            testsuite = L3BUILD_TESTSUITES[name]
        else:
            if testsuite is None:
                for ts in L3BUILD_TESTSUITES.values():
                    if name in ts.resolve_tests():
                        testsuite = ts
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

    match target:
        case 'check':
            pass
        case 'test':
            pass

    if testsuite is not None:
        if names:
            print(f"[l3build.py] Ignoring arguments: {', '.join(names)}")
        options.append(f'-c{testsuite.config}')
        print(f'cd {testsuite.path}')

    print(f'l3build {target} {" ".join(options)} {" ".join(names)}')

    # print()
    # if testsuite is not None:

    # command = args.popleft()
    # pprint(command)
    # pprint(args)

parser = argparse.ArgumentParser(
    description='A l3build wrapper',
    allow_abbrev=False,
)
parser.add_argument('target', type=str, choices=L3BUILD_COMMANDS, help='The l3build target to run')
parser.add_argument('-a', '--all', action='store_true', default=False)
parser.add_argument('-e', '--engine', type=str)
parser.add_argument('-s', '--stdengine', action='store_true', default=False)
parser.add_argument('-q', '--quiet', action='store_true', default=True)

if __name__ == "__main__":
    # print("Hello, world!")

    # from pprint import pprint

    args, unknown_args = parser.parse_known_intermixed_args()
    pprint(args)
    pprint(unknown_args)
    print()

    parse_args(args, unknown_args)
    # parse_args(args.args)
    # pprint(args.args)
    # for ts in testsuites:
    #     pprint(ts)
