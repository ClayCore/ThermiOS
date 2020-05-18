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
import colorama
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
from typing import List
from docopt import docopt, DocoptExit
from pathlib import Path
from dotenv import load_dotenv
from logger import Logger


class Builder(utils.Base):
    def __init__(self):
        # The following super class gives us
        # the basic variables, like the project root and stuff like this
        super().__init__()

        # Paths to libraries
        self.libs_dir = self.project_root / 'libs'
        self.libc_dir = self.libs_dir / 'LibC'

        # Utility libraries and sources
        self.src_dir = self.project_root / 'src'

        # Sysroot directory
        self.sysroot_dir = self.project_root / self.sysroot_var

        # Toochain directory
        # this is where the compilers live
        self.toolchain_dir = self.project_root / self.prefix_var / 'bin'

        self.build_dir = self.project_root / 'build'
        self.install_dir = self.sysroot_dir / 'build'

    def cleanup(self):
        Logger.pinfo('Initializing clean-up...', start='\n')

        # Cleans all the mess up
        clean_dirs = [self.build_dir, self.install_dir]

        for path in clean_dirs:
            utils.clean_dir(path)

        Logger.pinfo('Clean-up completed succesfully', start='\n')

    def get_file_list(self, path: Path, pattern: str) -> List[Path]:
        return sorted(path.glob(pattern))

    def src_map_files(self):
        Logger.pinfo('Mapping out all the filetypes to their respective lists...', start='\n')
        headers_lib = self.get_file_list(self.libs_dir, '**/*.h')
        headers_src = self.get_file_list(self.src_dir, '**/*.h')
        self.headers = utils.combine_list(headers_lib, headers_src)

        sources_lib = self.get_file_list(self.libs_dir, '**/*.cc')
        sources_src = self.get_file_list(self.src_dir, '**/*.cc')
        self.sources = utils.combine_list(sources_lib, sources_src)

        assembly_lib = self.get_file_list(self.libs_dir, '**/*.s')
        assembly_src = self.get_file_list(self.src_dir, '**/*.s')
        self.assemblies = utils.combine_list(assembly_lib, assembly_src)

        # Map files are compiled sources of the kernel.
        map_files = self.get_file_list(self.src_dir, '**/*.map')

        self.include_dirs = [self.libs_dir, self.src_dir]

    def make_build_dirs(self):
        Logger.pinfo('Building the source code...', start='\n')

        compiler = self.toolchain_dir / f'{self.target}-g++'
        assembler = self.toolchain_dir / f'{self.target}-as'
        linker = self.toolchain_dir / f'{self.target}-ld'

        sources = dict(zip(self.sources, self.assemblies))
        for source, assembly in sources.items():
            assembly_obj = self.build_dir / assembly.name.replace('.s', '.o')
            source_obj = self.build_dir / source.name.replace('.cc', '.o')

            assembly_cmd = [assembler, assembly, '-o', assembly_obj]
            sp.run(assembly_cmd)

            additional_src_args = ['-ffreestanding', '-O2', '-Wall', '-Wextra', '-fno-exceptions', '-fno-rtti', '--std=c++17', '-nostdlib', '-lgcc', '-nostartfiles']
            source_cmd = [compiler, source, '-o', source_obj, f'-I{self.libc_dir.resolve()}', *additional_src_args]
            sp.run(source_cmd)

            additional_args = ['-O2', '-nostdlib', '-lgcc', '-ffreestanding', '-fno-rtti', '-fno-exceptions', '-std=c++17']
            image_cmd = [compiler, '-T', self.src_dir / 'MainLinker.ld', '-o', self.build_dir / 'thermios.bin', source_obj, assembly_obj, *additional_args]
            sp.run(image_cmd)


def main():
    builder = Builder()
    args = docopt(__doc__, version=builder.get_version_number(), options_first=True)

    if args['full'] is True:
        builder.src_map_files()
        builder.make_build_dirs()

    elif args['clean'] is True:
        print('Clean')
    elif args['sync'] is True:
        print('Sync')
    elif args['map'] is True:
        print('Map')
    elif args['build'] is True:
        print('Build')
    else:
        Logger.perror('Unhandled option!')
        Logger.exit(errno.EINVAL)


if __name__ == '__main__':
    colorama.init()
    Logger.pinfo('Running build script...')
    if len(sys.argv) == 1:
        # automatically append `--help` to argv
        # if no launch arguments were provided
        sys.argv.append('--help')

    main()
