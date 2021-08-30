import importlib.abc
import os
import sys
from typing import Dict, Optional, Tuple
import types


FINDER_AND_LOADER_MODULE_NAME = 'CUSTOM_LOADER'
DEFAULT_PACKAGE_NAME = 'pyterpreter'


class FinderAndLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, packages: Dict[str, Tuple[bool, int, int, int]], source: str):
        self.packages = packages
        self.source = source

    # TODO if this is needed in future (use sys.excepthook = self.excepthook in __init__)
    # @staticmethod
    # def excepthook(exception_type, value, traceback):
    #     import traceback as tb
    #     tb.print_exception(exception_type, value, traceback)

    def find_module(self, fullname: str, path: Optional[str]) -> Optional['FinderAndLoader']:
        if fullname in self.packages.keys():
            return self

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

            code = self.source[code_start: code_end]
            compiled_code = compile(code, module.__file__, 'exec')
            exec(compiled_code, module.__dict__)

            return module
        except Exception as ex:
            raise ImportError(f'Error loading {fullname} with custom loader: {ex}')


def prepare_package():
    packages = {
        "pyterpreter.communication": (False, 2788, 4792, 1630331742),
        "pyterpreter.message_processor": (False, 4792, 7800, 1629365020),
        "pyterpreter.config": (False, 7800, 7959, 1630232026),
        "pyterpreter": (True, 7959, 8067, 1626595632),
        "pyterpreter.util": (False, 8067, 8816, 1630331749),
        "pyterpreter.run": (False, 8816, 9072, 1630331728),
        "core.message": (False, 9072, 10686, 1626681783),
        "core": (True, 10686, 10686, 1624097201),
    }

    # Get the entire source_code of this file
    # If executed as python3 main.py the source_code is obtained by reading the __file__ global
    # If executed via stdin (ie __file__ is not defined) then the source_code must be set as the __source_code__ global
    # file = globals().get('__file__')
    # file = 'one_file_1.py'
    file = None
    source_code = globals().get('__source_code__')
    if file is not None:
        with open(os.path.splitext(file)[0] + '.py') as fh:
            source_code = fh.read()
    elif source_code is None:
        raise Exception('file and source are both none. The global __source__ must be set if run directly from the python interpreter')

    # Add the custom FinderAndLoader (including entire source_code) to the system finder list (sys.meta_path)
    finder_and_loader = FinderAndLoader(packages, source_code)
    sys.meta_path.append(finder_and_loader)

    # Compile and run the default packages code
    default_package_code_start, default_package_code_end = packages[DEFAULT_PACKAGE_NAME][1:3]
    default_package_code = source_code[default_package_code_start: default_package_code_end]
    print(f'Running default package code\n{default_package_code}')
    default_package_init_filename = DEFAULT_PACKAGE_NAME + '/__init__.py'
    compiled_code = compile(default_package_code, default_package_init_filename, 'exec')
    new_globals = {
        '__file__': default_package_init_filename,
        '__name__': __name__,
        '__loader__': finder_and_loader,
    }
    exec(compiled_code, new_globals)


# Prepare loader's module and populate this namespace only with package's
# __init__
prepare_package()
