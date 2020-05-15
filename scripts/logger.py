#!/usr/bin/env python3
# Utility module for logging

import sys
import errno
import os
from colorama import Style, Fore


class Logger(object):
    @staticmethod
    def exit(error):
        sys.exit(os.strerror(error))

    @staticmethod
    def debug(msg):
        return f'{Style.BRIGHT}{Fore.CYAN}[DEBUG]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def pdebug(msg, start=''):
        print(f'{start}{Logger.debug(msg)}')

    @staticmethod
    def info(msg):
        return f'{Style.BRIGHT}{Fore.GREEN}[INFO]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def pinfo(msg, start=''):
        print(f'{start}{Logger.info(msg)}')

    @staticmethod
    def warn(msg):
        return f'{Style.BRIGHT}{Fore.YELLOW}[WARN]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def pwarn(msg, start=''):
        print(f'{start}{Logger.warn(msg)}')

    @staticmethod
    def error(msg):
        return f'{Style.BRIGHT}{Fore.RED}[ERROR]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def perror(msg, start=''):
        print(f'{start}{Logger.error(msg)}')
