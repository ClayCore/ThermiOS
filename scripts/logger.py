#!/usr/bin/env python3
# Utility module for logging

import sys
import errno
import os
from datetime import datetime
from colorama import Style, Fore


class Logger(object):
    @staticmethod
    def get_time():
        now = datetime.now()
        current_time = now.strftime('%H:%M:%S')
        return current_time

    @staticmethod
    def exit(error):
        sys.exit(os.strerror(error))

    @staticmethod
    def debug(msg):
        return f'{Style.BRIGHT}{Fore.CYAN}[DEBUG/{Logger.get_time()}]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def pdebug(msg, start=''):
        print(f'{start}{Logger.debug(msg)}')

    @staticmethod
    def info(msg):
        return f'{Style.BRIGHT}{Fore.GREEN}[INFO/{Logger.get_time()}]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def pinfo(msg, start=''):
        print(f'{start}{Logger.info(msg)}')

    @staticmethod
    def warn(msg):
        return f'{Style.BRIGHT}{Fore.YELLOW}[WARN/{Logger.get_time()}]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def pwarn(msg, start=''):
        print(f'{start}{Logger.warn(msg)}')

    @staticmethod
    def error(msg):
        return f'{Style.BRIGHT}{Fore.RED}[ERROR/{Logger.get_time()}]: {Style.NORMAL}{Fore.WHITE}{msg}{Style.RESET_ALL}'

    @staticmethod
    def perror(msg, start=''):
        print(f'{start}{Logger.error(msg)}')
