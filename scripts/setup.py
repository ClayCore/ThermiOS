#!/usr/bin/env python3

'''Claymore's setup script

Sets up environmental variables, project_root,
downloads and sets up the cross-compile toolchain,
prepares directory structures and more.

Usage:
    setup.py [--help]
    setup.py full
    setup.py clean
    setup.py download
    setup.py extract
    setup.py configure
    setup.py build

Options:
    --help              Shows this screen.

Subcommands:
    full                Runs clean, download, extract, configure and build in sequence.
    clean               Cleans all the build, cache, downloads and toolchain directories.
    download            Downloads the toolchain.
    extract             Extracts the downloaded tarballs.
    configure           Configures extracted tools.
    build               Builds the configured cross-compiling toolchain.
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


class Installer(object):
    def __init__(self):
        self.config_filename = 'config.yaml'
        self.project_root = self.find_project_root()
        self.config_file = self.project_root / self.config_filename
        self.config = self.get_config_data()

        # User configuration
        self.program_name = self.get_config_var('program_name')
        self.version = self.get_config_var('version')
        self.arch = self.get_config_var('arch')
        self.target = self.get_config_var('target')
        self.gcc_version = self.get_config_var('gcc_version')
        self.binutils_version = self.get_config_var('binutils_version')
        self.sysroot_var = self.get_config_var('sysroot')
        self.prefix_var = self.get_config_var('prefix')

        # Toolchain paths
        # NOTE: the hash is only valid for the latest gcc version.
        # It must be updated in the case that we change the version or else, it's going to fail
        # The same goes for the binutils hash.
        self.gcc_file = f'gcc-{self.gcc_version}'
        self.gcc_url = f'https://ftp.gnu.org/gnu/gcc/gcc-{self.gcc_version}/{self.gcc_file}.tar.xz'
        self.gcc_hash = '7d48e00245330c48b670ec9a2c518291'

        self.binutils_file = f'binutils-{self.binutils_version}'
        self.binutils_url = f'https://ftp.gnu.org/gnu/binutils/{self.binutils_file}.tar.xz'
        self.binutils_hash = '664ec3a2df7805ed3464639aaae332d6'

        # Directory structure
        self.sysroot_dir = self.project_root / self.sysroot_var
        self.prefix_dir = self.project_root / self.prefix_var
        self.toolchain_dir = self.project_root / 'toolchain'
        self.downloads_dir = self.toolchain_dir / 'downloads'
        self.source_dir = self.toolchain_dir / 'src'
        self.build_dir = self.toolchain_dir / 'build'

    def get_version_number(self):
        return self.version

    def check_path(self, path):
        # Utility function for checking if a given path exists
        if not path.exists():
            Logger.perror(f'Cannot find [{path.name}]')
            Logger.exit(errno.ENOENT)

    def md5_compare(self, path):
        # Returns true if the two hashes, of the local file
        # and the hardcoded hash, match
        md5_file = hashlib.md5()

        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                md5_file.update(chunk)
            md5_result = md5_file.hexdigest()
            Logger.pdebug(f'{md5_result}')
            if 'gcc' in str(path):
                if md5_result == self.gcc_hash:
                    return True
                else:
                    return False
            else:
                if md5_result == self.binutils_hash:
                    return True
                else:
                    return False

    def find_project_root(self):
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

    def get_config_data(self):
        # Loads the entire config using the yaml loader
        Logger.pinfo('Loading project configuration...', start='\n')
        with open(self.config_file) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        if data is None:
            Logger.perror('Could not parse configuration or empty config.yaml')
            Logger.exit(errno.EBADF)

        else:
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

    def get_config_var(self, key):
        # Internally calls into find_config_var and returns the given
        # config file we're looking for
        for result in self.find_config_var(key, self.config):
            if result is None:
                Logger.perror(f'[{key}] not found in config!')
                Logger.exit(errno.ENODATA)
            else:
                Logger.pdebug(f'[{key}] is [{result}]')
                return result

    def make_toolchain_dirs(self):
        Logger.pinfo(f'Creating additional directories...', start='\n')

        dirs = [self.sysroot_dir, self.toolchain_dir, self.downloads_dir,
                self.source_dir, self.build_dir, self.prefix_dir]
        for folder in dirs:
            if not folder.exists():
                try:
                    Logger.pdebug(f'Created [{folder.parent}/{folder.name}]')
                    folder.mkdir()
                except Exception as err:
                    Logger.perror(f'Could not create directory [{folder.name}] at [{folder}]: {err}')
                    Logger.exit(errno.EPERM)

        # NOTE: this step is necessary, because gcc and binutils
        # will look for this directory and NOT BUILD, for whatever reason
        # if it's not present.
        include_dir = Path(self.prefix_dir / f'{self.arch}/sys-root/usr/include')
        if not include_dir.exists():
            include_dir.mkdir(parents=True)

    def download_tools(self):
        # Make sure we have the directories required
        self.make_toolchain_dirs()

        Logger.pinfo(f'Downloading tarballs...', start='\n')

        paths = [self.gcc_file, self.binutils_file]
        urls = [self.gcc_url, self.binutils_url]
        tools = dict(zip(paths, urls))

        for path, url in tools.items():
            path_ext = f'{path}.tar.xz'
            download_path = self.downloads_dir / path_ext

            # Get the cross compile toolchain path
            extract_path = self.source_dir / path

            if extract_path.exists():
                # if everything exists, don't validate and re-download sources
                Logger.pwarn(f'[{download_path.name}] already exists at [{self.source_dir}]')
            elif not download_path.exists():
                # if they do not exist, just download them
                with open(download_path, 'wb') as file:
                    response = requests.get(url)

                    # Get length and stuff like this for the progress bar
                    length = response.headers.get('content-length')
                    utils.print_progress(0, int(length), prefix='Progress:', suffix='Complete', length=50)
                    if length is None:
                        Logger.pwarn('Could not retrieve length of data stream from response!')
                        file.write(response.content)
                    else:
                        dl = 0
                        for data in response.iter_content(chunk_size=4096):
                            dl += len(data)
                            self.print_progress(dl, int(length), prefix='Progress:', suffix='Complete', length=50)
                            file.write(data)
                Logger.pdebug(f'Succesfully downloaded [{download_path.name}]', start='\n')
            else:
                # Make sure the existing archives have identical hashes
                # For some reason md5_compare takes a really long time...
                Logger.pwarn(f'[{download_path.name}] already present!')
                Logger.pinfo(f'Checking if files are identical... (this may take a while)')
                result = self.md5_compare(download_path)
                if result is False:
                    Logger.perror(f'Files have different hashes! Cleaning downloads directory and re-running the script!')
                    utils.clean_dir(self.downloads_dir)
                    self.download_tools()

    def extract_tarball(self, path):
        # Extract the tools and move the unecessary tarball to the cache folder
        with lzma.open(path) as file:
            with tarfile.open(fileobj=file) as tar:
                content = tar.extractall(path=self.source_dir)

        Logger.pdebug(f'Succesfully extracted [{path.name}] to [{self.source_dir.name}]')

    def cleanup(self):
        Logger.pinfo('Initializing clean-up...', start='\n')

        # Cleans all the mess up
        clean_dirs = [self.build_dir, self.source_dir, self.downloads_dir, self.toolchain_dir]

        for path in clean_dirs:
            utils.clean_dir(path)

        Logger.pinfo('Clean-up completed succesfully', start='\n')

    def extract_tools(self):
        Logger.pinfo('Extracting tarballs..', start='\n')
        # Extracts all the tools from the source directory
        gcc_path = self.downloads_dir / f'{self.gcc_file}.tar.xz'
        binutils_path = self.downloads_dir / f'{self.binutils_file}.tar.xz'
        paths = [gcc_path, binutils_path]

        for path in paths:
            self.extract_tarball(path)

        Logger.pinfo('Toolchain extracted succesfully!', start='\n')

    def configure_toolchain(self):
        # Configures the toolchain
        # using a list of `sane` arguments for each tool
        #
        # NOTE: if you're unhappy, would like to build with different libraries
        # or something else, you can change it here.
        Logger.pinfo('Configuring the toolchain...', start='\n')

        # Configure and later `make` is going to complain if we
        # don't have prefix/bin in the path. add it for this session.
        # NOTE: you should already have it in path if you follow the build instructions...
        bin_dir = str(Path(self.prefix_dir / 'bin').resolve())
        if not bin_dir in os.environ['PATH']:
            Logger.pdebug(f'Adding [{bin_dir}] to $PATH')
            os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']

        # Assemble a list of source and configure paths.
        # GCC and binutils will NOT build in their source directories, so we're using
        # The `build/` directory for that.
        binutils_path = self.source_dir / self.binutils_file
        gcc_path = self.source_dir / self.gcc_file

        binutils_cwd = self.build_dir / self.binutils_file
        gcc_cwd = self.build_dir / self.gcc_file

        # Check if the following paths exist.
        self.check_path(binutils_path)
        self.check_path(gcc_path)

        if not binutils_cwd.exists():
            binutils_cwd.mkdir()

        if not gcc_cwd.exists():
            gcc_cwd.mkdir()

        binutils_configure_path = binutils_path / 'configure'
        binutils_configure_cmd = [
            binutils_configure_path, f'--prefix={self.prefix_dir}',
            f'--target={self.target}', '--with-sysroot', '--disable-nls'
        ]

        gcc_configure_path = gcc_path / 'configure'
        gcc_configure_cmd = [
            gcc_configure_path, f'--prefix={self.prefix_dir}',
            f'--target={self.target}', f'--with-sysroot', '--disable-nls',
            '--without-headers', '--enable-languages=c,c++'
        ]

        sp.run(binutils_configure_cmd, cwd=binutils_cwd, stdout=sp.DEVNULL)
        sp.run(gcc_configure_cmd, cwd=gcc_cwd, stdout=sp.DEVNULL)

        Logger.pinfo('Toolchain configured succesfully!', start='\n')

    def build_tools(self):
        Logger.pinfo('Building configured tools', start='\n')
        binutils_path = self.build_dir / self.binutils_file
        gcc_path = self.build_dir / self.gcc_file

        self.check_path(binutils_path)
        self.check_path(gcc_path)

        binutils_build_cmd = [
            'make', f'-j{os.cpu_count()}'
        ]
        sp.run(binutils_build_cmd, cwd=binutils_path, stdout=sp.DEVNULL)

        binutils_install_cmd = [
            'make', 'install'
        ]
        sp.run(binutils_install_cmd, cwd=binutils_path, stdout=sp.DEVNULL)

        gcc_build_cmd = [
            'make', f'-j{os.cpu_count()}', 'all-gcc', 'all-target-libgcc'
        ]
        sp.run(gcc_build_cmd, cwd=gcc_path, stdout=sp.DEVNULL)

        gcc_install_cmd = [
            'make', 'install-gcc', 'install-target-libgcc'
        ]
        sp.run(gcc_install_cmd, cwd=gcc_path, stdout=sp.DEVNULL)


def main():
    installer = Installer()
    args = docopt(__doc__, version=installer.get_version_number(), options_first=True)

    if args['full'] is True:
        installer.cleanup()
        installer.download_tools()
        installer.extract_tools()
        installer.configure_toolchain()
        installer.build_tools()
    elif args['clean'] is True:
        installer.cleanup()
    elif args['download'] is True:
        installer.download_tools()
    elif args['extract'] is True:
        installer.extract_tools()
    elif args['configure'] is True:
        installer.configure_toolchain()
    elif args['build'] is True:
        installer.build_tools()
    else:
        Logger.perror('Unhandled option!')
        Logger.exit(errno.EINVAL)


if __name__ == '__main__':
    Logger.pinfo('Initializing the setup script...')
    if len(sys.argv) == 1:
        # automatically append `--help` to argv
        # if no launch arguments were provided
        sys.argv.append('--help')

    main()
