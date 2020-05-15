#!/usr/bin/env python3

'''Claymore's build script

Builds all the libraries and sources.

Usage:
    build.py [--help]
    build.py full
    build.py clean
    build.py sync
    build.py map
    build.py build

Options:
    --help              Shows this screen.

Subcommands:
    full                Runs all the commands below in sequence.
    clean               Cleans all the build directories, object files, etc.
    sync                Incremental build.
    map                 Creates a kernel.map file by building the entire kernel
    build               Builds every source file in the project.
'''

# Various imports
import sys
import errno
import os
import shutil
import tarfile
import lzma
import yaml
import requests
import hashlib
import subprocess as sp
import time
import utils
from docopt import docopt, DocoptExit
from pathlib import Path
from dotenv import load_dotenv
from logger import Logger


class Builder(object):
    def __init__(self):
        pass


def main():
    builder = Builder()
    args = docopt(__doc__, version='0.0.1', options_first=True)


if __name__ == '__main__':
    Logger.pinfo('Running build script...')
    if len(sys.argv == 1):
        # automatically append `--help` to argv
        # if no launch arguments were provided
        sys.argv.append('--help')

    main()
