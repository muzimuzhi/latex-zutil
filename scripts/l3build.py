#!/usr/bin/env -S uv run --script

import argparse
from pathlib import Path
from subprocess import run


class TestSuite:
    def __init__(self, name: str, directory: str, config: str, tests: tuple[str]) -> None:
        self.name = name
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
    directory = 'tabularray',
    config = 'build',
    tests = ('testfiles/*.lvt',)
)

tblr_old = TestSuite(
    name = 'tabularray-old',
    directory = 'tabularray',
    config = 'config-old',
    tests = ('testfiles-old/*.tex',)
)

L3BUILD_COMMANDS = ('check', 'save')
L3BUILD_TESTSUITES = {
    zutil.name: zutil,
    tblr.name: tblr,
    tblr_old.name: tblr_old,
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
        name_raw = name
        name = resolve_name_alias(name)
        if name.startswith('-'):
            raise ValueError(f"Unknown argument: {name}")
        # elif name in L3BUILD_TESTSUITES:
        #     ts = L3BUILD_TESTSUITES[name]
        #     testsuite = L3BUILD_TESTSUITES[name]
        else:
            for ts in L3BUILD_TESTSUITES.values():
                if name == ts.name:
                    if testsuite is None:
                        testsuite = ts
                    elif testsuite != ts:
                        raise ValueError(f"Multiple testsuites: testsuite {name_raw} doesn't contain tests {names}")
                    else:
                        names = []
                    break
                if name in ts.resolve_tests():
                    if testsuite is None:
                        testsuite = ts
                    elif testsuite != ts:
                        raise ValueError(f"Multiple testsuites: test {name} is not in testsuite {testsuite.directory}")
                    if name not in names:
                        names.append(name)
                    break
            else:
                raise ValueError(f"Unknown test name: {name}")

    if testsuite is None:
        raise ValueError("No testsuite recognized.")

    # compose l3build options
    if args.engine:
        options.append(f'-e{args.engine}')
    if args.stdengine:
        options.append('-s')
    if args.quiet:
        options.append('-q')
    if testsuite.config != 'build':
        options.append(f'-c{testsuite.config}')

    # 'save' target without names means saving all
    if target == 'save' and not names:
        names = testsuite.resolve_tests()

    commands = ['l3build', target, *options, *names]
    if args.dry_run:
        print(f"[l3build.py] Running '{' '.join(commands)}' in directory '{testsuite.directory}'")
    else:
        run(commands, cwd=testsuite.directory)

parser = argparse.ArgumentParser(
    description='A l3build wrapper',
    allow_abbrev=False,
)
parser.add_argument('target', type=str, choices=L3BUILD_COMMANDS, help='The l3build target to run')
# inherited frequently-used l3build options
# Unlike in vanilla l3build.lua, options can be intermixed with test names,
# and uses like `-qs` are accepted.
parser.add_argument('-e', '--engine', type=str)
parser.add_argument('-s', '--stdengine', action='store_true', default=False)
parser.add_argument('-q', '--quiet', action='store_true', default=True)
# new options
parser.add_argument('-n', '--dry-run', action='store_true', default=False)


if __name__ == "__main__":
    args, unknown_args = parser.parse_known_intermixed_args()
    parse_args(args, unknown_args)
