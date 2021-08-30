import importlib.abc
import os
import sys
import types

from typing import Dict, Tuple, Optional


class FinderAndLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, packages: Dict[str, Tuple[bool, int, int, int]], source_filename: str):
        self.packages = packages
        self.filename = source_filename
        # sys.excepthook = self.excepthook

    # @staticmethod
    # def excepthook(exception_type, value, traceback):
    #     import traceback as tb
    #     tb.print_exception(exception_type, value, traceback)

    def find_module(self, fullname: str, path: Optional[str]) -> Optional['FinderAndLoader']:
        print(f'Looking for finder for {fullname}')
        if fullname in self.packages.keys():
            print(f'Found loader for {fullname}')
            return self

    @staticmethod
    def _get_code(filename: str, start: int, end: int):
        print(f'Getting code from {filename}: {start}-{end}')
        with open(filename) as fh:
            fh.seek(start)
            return fh.read(end - start)

    def load_module(self, fullname):
        try:
            if fullname in sys.modules.keys():
                return sys.modules[fullname]

            is_package, code_start, code_end, timestamp = self.packages[fullname]

            module = types.ModuleType(fullname)
            module.__loader__ = self
            path = fullname.replace('.', '/')

            if is_package:
                module.__package__ = fullname
                module.__file__ = os.path.join(path, '__init__.py')
                module.__path__ = [path]
            else:
                module.__package__ = fullname.rsplit('.', 1)[0]
                module.__file__ = path + '.py'

            sys.modules[fullname] = module

            code = self._get_code(self.filename, code_start, code_end)
            compiled_code = compile(code, module.__file__, 'exec')
            exec(compiled_code, module.__dict__)

            return module
        except Exception as ex:
            raise ImportError(f'Error loading {fullname} with custom loader\n{ex}')
