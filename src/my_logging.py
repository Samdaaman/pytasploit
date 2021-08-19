from typing import Callable, Optional

from colorama import Fore, Style
import traceback


class Logger:
    def __init__(self, name: str):
        self.name = name

    def _print(self, line: str, colour: Fore, formatted=True):
        print(f'{colour}{f" *** [{self.name}] " if formatted else ""}{line}{Style.RESET_ALL}')

    def info(self, line: str):
        self._print(line, Fore.GREEN)

    def debug(self, line: str):
        self._print(line, Fore.BLUE)

    def warn(self, line: str):
        self._print(line, Fore.RED)

    def output(self, line: str):
        self._print(line, Fore.YELLOW, False)

    def error(self, location: str, description=None):
        if description is None:
            description = traceback.format_exc()
        self._print(f'Error in {location}: \n{description}', Fore.LIGHTRED_EX)
