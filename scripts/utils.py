#!/usr/bin/env python3

# Utility module

import os
import shutil
import errno
from pathlib import Path
from logger import Logger

# Moves a file from the source location to the destination


def move_file(src: Path, dest: Path):
    return src.replace(dest)


def print_progress(index, total, prefix='', suffix='', decimals=1, length=100, fill='#', end='\r'):
    # Prints a progress bar when downloading the tools.
    # NOTE: fix to make it actually work
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (index / float(total)))
    filled_len = int(length * index // total)
    bar = fill * filled_len + '-' * (length - filled_len)
    bar_full = f'{prefix} |{bar}| {percent}% {end}'
    sys.stdout.write(f'\r{Logger.info(bar_full)}')
    sys.stdout.flush()
    if index == total:
        print()


# Cleans a given path and all its subdirectories and files
def clean_dir(path):
    if path.exists():
        for file in path.iterdir():
            try:
                if file.is_file() or file.is_symlink():
                    file.unlink()
                elif file.is_dir():
                    shutil.rmtree(file)
            except FileNotFoundError as err:
                Logger.perror(f'Could not remove file or directory at [{file}]')
                Logger.perror(f'{err}')
            except BlockingIOError:
                Logger.perror(f'Resource is likely busy!')
                Logger.pexit(errno.EBUSY)
        if path.is_dir():
            try:
                shutil.rmtree(path)
            except FileNotFoundError as err:
                Logger.perror(f'Could not directory at [{path}]')
                Logger.perror(f'{err}')
