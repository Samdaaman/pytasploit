from base64 import b64decode
import importlib.abc
import os
import sys
from typing import Dict, Optional, Tuple
import types


FINDER_AND_LOADER_MODULE_NAME = 'CUSTOM_LOADER'
DEFAULT_PACKAGE_NAME = '<DEFAULT_PACKAGE_NAME_INSERTED_HERE>'


class FinderAndLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, packages: Dict[str, Tuple[bool, str]]):
        self.packages = packages

    # TODO if this is needed in future (use sys.excepthook = self.excepthook in __init__)
    # @staticmethod
    # def excepthook(exception_type, value, traceback):
    #     import traceback as tb
    #     tb.print_exception(exception_type, value, traceback)

    def find_module(self, full_package_name: str, path: Optional[str]) -> Optional['FinderAndLoader']:
        if full_package_name in self.packages.keys():
            return self

    def load_module(self, full_package_name):
        try:
            if full_package_name in sys.modules.keys():
                return sys.modules[full_package_name]

            is_package, code = self.packages[full_package_name]

            module = types.ModuleType(full_package_name)
            module.__loader__ = self
            path = full_package_name.replace('.', '/')

            if is_package:
                module.__package__ = full_package_name
                module.__file__ = os.path.join(path, '__init__.py')
                module.__path__ = [path]
            else:
                module.__package__ = full_package_name.rsplit('.', 1)[0]
                module.__file__ = path + '.py'

            if globals().get('__source__') is not None:
                module.__source__ = globals()['__source__']  # allow __source__ global to be passed down to modules

            sys.modules[full_package_name] = module

            compiled_code = compile(code, module.__file__, 'exec')
            exec(compiled_code, module.__dict__)

            return module
        except Exception as ex:
            raise ImportError(f'Error loading {full_package_name} with custom loader: {ex}')


def main():
    packages: Dict[str, Tuple[bool, str]] = {
        # <PACKAGES_INSERTED_HERE>
    }

    for package_name in packages.keys():
        packages[package_name] = (packages[package_name][0], b64decode(packages[package_name][1].encode()).decode())

    # Add the custom FinderAndLoader (including entire source_code) to the system finder list (sys.meta_path)
    finder_and_loader = FinderAndLoader(packages)
    sys.meta_path.append(finder_and_loader)

    # Compile and run the default packages code
    default_package_code = packages[DEFAULT_PACKAGE_NAME][1]
    default_package_init_filename = DEFAULT_PACKAGE_NAME + '/__init__.py'
    compiled_code = compile(default_package_code, default_package_init_filename, 'exec')
    new_globals = {
        '__file__': default_package_init_filename,
        '__name__': '__main__',
        '__loader__': finder_and_loader,
    }
    if globals().get('__source__') is not None:
        new_globals['__source__'] = globals()['__source__']  # allow __source__ global to be passed down to modules
    exec(compiled_code, new_globals)


main()
