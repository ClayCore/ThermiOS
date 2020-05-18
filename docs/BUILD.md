# ThermiOS build instructions.

## Dependencies

We only cover Linux-based environments here.

Debian/Ubuntu:

```bash
sudo apt install build-essential curl libmpfr-dev libmpc-dev libgmp-dev e2fsprogs qemu-system-i386 qemu-utils tar
```

Arch Linux:

```bash
sudo pacman -S base-devel curl mpfr libmpc gmp e2fsprogs qemu qemu-arch-extra tar
```

For running scripts you may require the following libraries:

```bash
pip install docopt python-dotenv colorama pyyaml --user
```

Notes:

-   The majority of the libraries are required to prepare the `binutils` and `gcc` cross-compile environment,
-   `qemu` is required to run the compiled OS,
-   Ensure you're running a Python version >= 3.7.2 to make sure you don't run into issues.

## Basic configuration

All the project and consequently build configuration is in the `/config.yaml` file.
It contains all necessary metadata for the `/scripts/setup.py` script.

`config.yaml:`

-   `program_name` and `version` is metadata for the project,
-   `arch` and `target` define the architecture of the OS and its _target-triplet_,
-   `prefix` is where the compiled toolchain will be installed to in relation to the _projects root folder_,
-   `sysroot` is the system root of the operating system, which is also where the system libraries and headers will be installed to
-   `gcc_version` and `binutils_version` are the version the setup script will install. Make sure they're actually compatible with each other and can be used in a cross-compile environment.
-   `build flags` will be the build flags for the compiler.

## Environmental variables

For the following commands and consequenently, the commands that they spawn, to do their job successfully, you have to update your environmental variables **before** running these scripts:

-   `$PREFIX` is the directory where your built toolchain will live, the default is present in the `/config.yaml` file and it's set to `/opt/`. Note that this is not your operating system's root `opt` directory, rather the project root.
-   `$TARGET` is the target architecture. The script will read this from the `/config.yaml`, so don't worry about it too much, but it's better to be safe and copy the default, which is `i686-elf` and export it as that env var.
-   `$PATH` must include the `$PREFIX/bin` directory

```bash
export PREFIX = <path to project root>/opt
export TARGET = i686-elf
export PATH = $PREFIX/bin:$PATH
```

## Running the setup and build scripts

After you get all the necessary dependencies and configure the project it's time to setup the workspace.

Navigate to the `/scripts/` directory and execute the following command:

```bash
python setup.py
```

You should get a help screen explaining all the subcommands. It's recommended you do a `full` install on your initial setup, so run:

```bash
python setup.py full
```

The script will now start parsing the `/config.yaml` file, downloading the tarballs, preparing the directory structure, extracting, configuring and building the toolchain. Optionally you can run the following command, **after** the full installation, to get rid of unnecessary intermediate folders.

```bash
python setup.py clean
```
