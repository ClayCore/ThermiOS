# Changelog

All notable changes to the project will be noted in this file

# [Unreleased]

---

## [0.0.1] 13-05-2020

### Added:

-   Basic directory structure:
    -   _Note_: the initial forward slash represents the **project root** not the filesystem root
    -   `/docs/` &rarr; reserved for crucial documentation of the project,
    -   '/libs/` &rarr; reserved for the standard C library reimplementation and other utility libraries,
    -   `/meta/` &rarr; for any metadata relevant to the repository,
    -   `/opt/` &rarr; where the finished and built toolchain will be present,
    -   `/scripts/` &rarr; reserved for various scripts, which automate certain tasks.
    -   `/src/` &rarr; where the source code of the operating system resides,
    -   `/sysroot/` &rarr; the operating system root,
    -   `/toolchain/` &rarr; a _temporary_ directory for the cross-compile toolchain.
-   Initial project configuration:
    -   `/config.yaml` &rarr; global project configuration,
    -   `/.clang-format` &rarr; global clang formatting utility configuration,
    -   `/.env` &rarr; project environmental variables, it's recommended to make sure your path is the same as the path in the .env file.
-   Basic documentation:
    -   `/CHANGELOG.md` &rarr; this document,
    -   `/README.md` &rarr; projects _README_,
    -   `/docs/BUILD.md` &rarr; explains how to build and run the operating system,
    -   `/docs/SCRIPTS.md` &rarr; explains the purpose of every script in the `/scripts` directory.
-   Basic setup scripts:
    -   `/scripts/logger.py` &rarr; utility module that allows for pretty logging to the terminal window,
    -   `/scripts/utils.py` &rarr; utility module that is basically a utility library, used by other scripts,
    -   `/scripts/setup.py` &rarr; downloads, extracts, ~~patches~~, builds and installs the cross-compile toolchain and sets up the project workspace with additional directories,
    -   `/scripts/build.py` &rarr; builds the kernel image and/or syncs the filesystem and creates the `kernel.map` file.
-   Initial source code:
    -   `/libs/LibC/` &rarr; home of the standard C library, reimplemented,
    -   `/libs/LibM/` &rarr; maths library, used by the standard C library,
    -   `/src/MainLinker.ld` &rarr; a basic LinkerScript configuration for the compiler and the build script,
    -   `/src/Vixen/*` &rarr; utility library.
