import os
import sys
import types

FINDER_AND_LOADER_MODULE_NAME = 'CUSTOM_LOADER'
DEFAULT_PACKAGE_NAME = 'pyterpreter'


def get_finder_and_loader_code() -> str:
    with open('finder_and_loader.py') as fh:
        return fh.read()


def prepare_package():
    packages = {
        "pyterpreter.communication": [
            0, 2788, 4792, 1630331742],
        "pyterpreter.message_processor": [
            0, 4792, 7800, 1629365020],
        "pyterpreter.config": [
            0, 7800, 7959, 1630232026],
        "pyterpreter": [
            1, 7959, 8067, 1626595632],
        "pyterpreter.util": [
            0, 8067, 8816, 1630331749],
        "pyterpreter.run": [
            0, 8816, 9072, 1630331728],
        "core.message": [
            0, 9072, 10686, 1626681783],
        "core": [
            1, 10686, 10686, 1624097201]
    }
    # If the loader code is not already loaded we create a specific module for
    # it.  We need to do it this way so that the functions in there are not
    # compiled with a reference to this module's global dictionary in
    # __globals__.
    finder_and_loader_module = types.ModuleType(FINDER_AND_LOADER_MODULE_NAME)
    finder_and_loader_module.__package__ = ''
    finder_and_loader_module.__file__ = FINDER_AND_LOADER_MODULE_NAME
    exec(get_finder_and_loader_code(), finder_and_loader_module.__dict__)
    sys.modules[FINDER_AND_LOADER_MODULE_NAME] = finder_and_loader_module

    # We cannot use __file__ directly because on the second run __file__ will
    # be the compiled file (.pyc) and that's not the file we want to read.
    source_filename = os.path.splitext(__file__)[0] + '.py'

    # finder_and_loader = finder_and_loader_module.FinderAndLoader(packages, source_filename)
    finder_and_loader = finder_and_loader_module.FinderAndLoader(packages, 'one_file_1.py')
    sys.meta_path.append(finder_and_loader)

    __, start, end, ts = packages[DEFAULT_PACKAGE_NAME]
    # with open(source_filename) as datafile:
    with open('one_file_1.py') as datafile:
        datafile.seek(start)
        code = datafile.read(end - start)

    # We need everything to be local variables before we clear the global dict
    name = __name__
    source_filename = DEFAULT_PACKAGE_NAME + '/__init__.py'
    compiled_code = compile(code, source_filename, 'exec')

    print(f'Running top level compiled code\n{code}')


    # Prepare globals to execute __init__ code
    globals().clear()
    # # If we've been called directly we cannot set __path__
    # if name != '__main__':
    #     globals()['__path__'] = [DEFAULT_PACKAGE_NAME]
    # else:
    #     def_package = None
    globals().update(__file__=source_filename, __name__=name, __loader__=finder_and_loader)

    exec(compiled_code, globals())


# Prepare loader's module and populate this namespace only with package's
# __init__
prepare_package()
