#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "colorama",
#   "tomlkit",
# ]
# ///

from pathlib import Path
from typing import Any

import argparse, logging, os, subprocess, sys  # noqa: E401
from colorama import Fore
from tomlkit import dumps, parse


logging.basicConfig(format=f'{Fore.LIGHTBLACK_EX}[%(name)s %(levelname)-5s]{Fore.RESET} %(message)s')
logger = logging.getLogger('wrapper')


def dry_run_print(*args: Any, **kwargs: Any) -> None:
    print(f'{Fore.LIGHTBLACK_EX}[wrapper DRY-RUN]{Fore.RESET}', *args, **kwargs)

parser = argparse.ArgumentParser(
    description="explcheck wrapper",
    usage='$(prog)s [options] files...',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '--config-file',
    default=os.getenv("EXPLCHECK_CONFIG", ".explcheck"),
    help='path to explcheck config file (default: .explcheck or env EXPLCHECK_CONFIG)'
)
parser.add_argument(
    '--config-line',
    action='append',
    default=[],
    help='set a config line (format: key=value, can be used multiple times)'
)
parser.add_argument(
    '--flow-analysis',
    action='store_true',
    help='force flow analysis'
)
parser.add_argument(
    '-n',
    '--dry-run',
    action='store_true',
    help='show what would run without executing'
)
parser.add_argument(
    '--debug',
    action='store_true',
    help='enable debug logging'
)


def main() -> None:
    argv = sys.argv[1:]
    if '--' in argv:
        # split args at '--'
        idx = argv.index('--')
        args_list = argv[:idx]
        args_remaining = argv[idx+1:]
    else:
        args_list = argv
        args_remaining = []
    args, args_unknown = parser.parse_known_args(args_list)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    config_old = args.config_file
    config_new = config_old
    if args.flow_analysis:
        args.config_line.append('stop_early_when_confused=false')

    if args.config_line:
        with open(config_old, "r") as config_file:
            toml_config = parse(config_file.read())

        for line in args.config_line:
            toml_line = parse(line)
            if 'defaults' in toml_line:
                toml_config['defaults'].update(toml_line['defaults'])
            else:
                toml_config['defaults'].update(toml_line)
        print(logger.getEffectiveLevel())
        logger.debug("patched config:")
        for line in dumps(toml_config).splitlines():
            logger.debug(line)

        config_new = config_new + ".tmp"
        with open(config_new, "w") as f:
            f.write(dumps(toml_config))

    # compose explcheck arguments to run
    cmd = ["explcheck", "--config-file", config_new]
    cmd.extend(args_unknown)
    cmd.extend(args_remaining)

    try:
        if args.dry_run:
            dry_run_print('run command', *cmd)
        else:
            print()
            subprocess.run(cmd, bufsize=0, check=True)
    except subprocess.CalledProcessError:
        pass
    finally:
        Path(config_new).unlink(missing_ok=True)

if __name__ == '__main__':
    main()
