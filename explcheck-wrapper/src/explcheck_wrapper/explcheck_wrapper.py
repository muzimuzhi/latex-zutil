from pathlib import Path
from typing import Literal, cast

import argparse
import logging
import os
import tempfile
import subprocess
import sys

from colorama import Fore, init
from difflib import unified_diff
# XXX choose tomlkit for its style-preserving feature.
#     But it only supports TOML 1.0, not 1.1 yet.
from tomlkit import TOMLDocument, dumps, table, parse
from tomlkit.items import Table


class LoggingFormatter(logging.Formatter):
    """Custom formatter to set different formats for different log levels."""

    FORMATS = {
        logging.DEBUG:    f'{Fore.LIGHTBLACK_EX}[%(name)s DEBUG]{Fore.RESET} %(message)s',
        logging.INFO:     f'{Fore.LIGHTBLACK_EX}[%(name)s  INFO]{Fore.RESET} %(message)s',
        logging.WARNING:  f'{Fore.LIGHTBLACK_EX}[%(name)s  WARN]{Fore.RESET} %(message)s',
        logging.ERROR:    f'{Fore.RED}[%(name)s ERROR]{Fore.RESET} %(message)s',
        logging.CRITICAL: f'{Fore.RED}[%(name)s  CRIT]{Fore.RESET} %(message)s'
    }

    def format(self, record):
        # Get the format for the current level or use a default
        if record.levelno <= logging.WARNING:
            default_format = self.FORMATS[logging.WARNING]
        else:
            default_format = self.FORMATS[logging.ERROR]
        log_fmt = self.FORMATS.get(record.levelno, default_format)
        # Create a temporary formatter with the chosen style
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def run(dry_run: bool, cmd) -> None:
    if dry_run:
        print(f'{Fore.LIGHTBLACK_EX}[wrapper DRY-RUN]{Fore.RESET}', *cmd)
    else:
        try:
            subprocess.run(cmd, bufsize=0, check=True, shell=True)
        except subprocess.CalledProcessError:
            pass


def merge_configs(
        config: TOMLDocument,
        config_patch: TOMLDocument,
        # 1st section is used as default section for unrecognized keys
        recognized_sections = ('defaults', 'filename', 'package'),
) -> TOMLDocument:
    for key, value in config_patch.items():
        if key in recognized_sections and isinstance(value, Table):
            section = key
            # XXX when 'value' is a table, this will replace the whole table
            _dict = value
        else:
            section = recognized_sections[0]
            _dict = table()
            _dict.append(key, value)
        if section not in config:
            config[section] = table()
        cast(Table, config[section]).update(_dict)
    return config


# based on https://github.com/tartley/colorama/issues/268#issuecomment-973315094
# https://no-color.org/
if (os.getenv('NO_COLOR') and os.getenv('NO_COLOR') != '') or \
    (os.getenv('CI') and os.getenv('CI') != ''):
    init(strip=True, convert=False)

# init logger
logger = logging.getLogger('wrapper')
ch = logging.StreamHandler()  # `ch` stands for `console handler`
ch.setFormatter(LoggingFormatter())
logger.addHandler(ch)


parser = argparse.ArgumentParser(
    description='explcheck wrapper',
    usage='$(prog)s [options] files...',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '--config-file',
    default=os.getenv('EXPLCHECK_CONFIG', '.explcheckrc'),
    help='path to explcheck config file (default: .explcheckrc or env EXPLCHECK_CONFIG)'
)
parser.add_argument(
    '--config-line',
    action='append',
    default=[],
    help='set a config line (format: key=value, can be used multiple times)'
)
parser.add_argument(
    '--flow-analysis',
    dest='config_line',
    action='append_const',
    const='stop_early_when_confused=false',
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

    config_file = args.config_file
    config_file_new = config_file
    if args.config_line:
        with open(config_file, 'r') as config_old:
            config_old_content = config_old.read()
            toml_config = parse(config_old_content)

        for line in args.config_line:
            toml_line = parse(line)
            merge_configs(toml_config, toml_line)

        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', prefix='explcheck_', suffix='.toml', delete=False) as f:
            config_new_content = dumps(toml_config)
            f.write(config_new_content)
            config_file_new = f.name

            if logger.getEffectiveLevel() <= logging.DEBUG:
                logger.debug('patched config:')
                diff = unified_diff(
                    config_old_content.splitlines(),
                    config_new_content.splitlines(),
                    fromfile=config_file,
                    tofile=config_file_new,
                    lineterm='',
                )
                for line in diff:
                    if line.startswith('+'):
                        logger.debug(f'{Fore.GREEN}{line}{Fore.RESET}')
                    elif line.startswith('-'):
                        logger.debug(f'{Fore.RED}{line}{Fore.RESET}')
                    else:
                        logger.debug(line)

    # compose explcheck arguments to run
    prog = os.getenv('EXPLCHECK_BIN', 'explcheck')
    cmd = [prog, '--config-file', config_file_new]
    cmd.extend(args_unknown)
    cmd.extend(args_remaining)

    run(args.dry_run, cmd)
    if args.config_line:
        Path(config_file_new).unlink()

if __name__ == '__main__':
    main()
