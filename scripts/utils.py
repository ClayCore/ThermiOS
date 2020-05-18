#!/usr/bin/env python3

# Utility module

import os
import shutil
import errno
import yaml
import sys
from typing import List
from dotenv import load_dotenv
from pathlib import Path
from logger import Logger


def combine_list(*argv):
    combined = list()
    for arg in argv:
        if arg:
            for file in arg:
                combined.append(file)

    if not combined:
        return None

    return sorted(combined)


def check_env(path: Path):
    load_dotenv(dotenv_path=path, override=True)


def move_file(src: Path, dest: Path) -> Path:
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
def clean_dir(path: Path):
    if path.exists():
        for file in os.listdir(path):
            filepath = path / file
            try:
                if filepath.is_file() or filepath.is_symlink():
                    filepath.unlink()
                elif filepath.is_dir():
                    shutil.rmtree(filepath)
            except FileNotFoundError as err:
                Logger.perror(f'Could not remove file or directory at [{filepath}]')
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


class Base(object):
    def __init__(self):
        self.config_filename = 'config.yaml'
        self.project_root = self.get_project_root_dir()
        self.config_file = self.project_root / self.config_filename
        self.config = self.get_config()

        # User configuration
        self.program_name = self.get_config_var('program_name')
        self.version = self.get_config_var('version')
        self.arch = self.get_config_var('arch')
        self.target = self.get_config_var('target')
        self.gcc_version = self.get_config_var('gcc_version')
        self.binutils_version = self.get_config_var('binutils_version')
        self.sysroot_var = self.get_config_var('sysroot')
        self.prefix_var = self.get_config_var('prefix')

    def check_path(self, path: Path):
        # Utility function for checking if a given path exists
        if not path.exists():
            Logger.perror(f'Cannot find [{path.name}]')
            Logger.exit(errno.ENOENT)

    def get_project_root_dir(self) -> Path:
        path = Path.cwd()
        Logger.pdebug(f'Currently in [{path}]', start='\n')

        max_dir_attempts = 5
        for _ in range(max_dir_attempts):
            # Go up the directory until you find the project root.
            # Which is determined by the location of the `config.yaml` file
            temp_root = path / self.config_filename
            project_root = path
            if temp_root.exists():
                Logger.pinfo(f'Project root found at [{project_root.resolve()}]')
                return project_root
            else:
                path = path.resolve().parent

        Logger.perror(f'Project root not found! Make sure you set the paths correctly!')
        Logger.exit(errno.ENOENT)

    def get_config(self) -> object:
        # Loads the entire config using the yaml loader
        Logger.pinfo('Loading project configuration...', start='\n')
        with open(self.config_file) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        if data is None:
            Logger.perror('Could not parse configuration or empty config.yaml')
            Logger.exit(errno.EBADF)

        return data

    def find_config_var(self, key, src):
        # Recursively goes through the yaml dump
        # and checks if a given value is dict, list or a result
        # we're looking for
        for k, v in (src.items() if isinstance(src, dict)
                     else enumerate(src) if isinstance(src, list)
                     else []):
            if k == key:
                yield v
            elif isinstance(v, (dict, list)):
                for result in self.find_config_var(key, v):
                    yield result

    def get_config_var(self, key: str) -> str:
        # Internally calls into find_config_var and returns the given
        # config file we're looking for
        for result in self.find_config_var(key, self.config):
            if result is None:
                Logger.perror(f'[{key}] not found in config!')
                Logger.exit(errno.ENODATA)
            else:
                Logger.pdebug(f'[{key}] is [{result}]')
                return result

    def get_version_number(self) -> str:
        return self.version
