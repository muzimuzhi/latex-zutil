#!/usr/bin/env -S uv run --script

import argparse
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestSuite:
    name: str
    path: Path
    test_patterns: tuple[str]
    # field wit a default value must be specified last
    config: str = 'build'

zutil = TestSuite(
    name = 'zutil',
    config = 'build',
    path = Path('zutil/testfiles'),
    test_patterns = ('zutil-*',)
)

tblr = TestSuite(
    name = 'tblr',
    path = Path('tblr/testfiles'),
    test_patterns = ('tblr-*',)
)

tblr_old = TestSuite(
    name = 'tblr-old',
    config = 'config-old',
    path = Path('tblr-old/testfiles-old'),
    test_patterns = ('*',)
)

testsuites = (
    zutil,
    tblr,
    tblr_old,
)

if __name__ == "__main__":
    print("Hello, world!")

    from pprint import pprint
    for ts in testsuites:
        pprint(ts)
