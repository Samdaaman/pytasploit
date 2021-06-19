import os
import sys
import types

PINLINED_DEFAULT_PACKAGE = 'pyterpreter'
PINLINER_MODULE_NAME = 'pinliner_loader'
loader_version = '0.2.1'

FORCE_EXC_HOOK = None

inliner_importer_code = '''
import imp
import marshal
import os
import struct
import sys
import types


class InlinerImporter(object):
    version = '%(loader_version)s'
    def __init__(self, data, datafile, set_excepthook=True):
        self.data = data
        self.datafile = datafile
        if set_excepthook:
            sys.excepthook = self.excepthook

    @staticmethod
    def excepthook(type, value, traceback):
        import traceback as tb
        tb.print_exception(type, value, traceback)

    def find_module(self, fullname, path):
        module = fullname in self.data
        if module:
            return self

    def get_source(self, fullname):
        __, start, end, ts = self.data[fullname]
        with open(self.datafile) as datafile:
            datafile.seek(start)
            code = datafile.read(end - start)
        return code

    def get_code(self, fullname, filename):
        py_ts = self.data[fullname][3]
        try:
            with open(fullname + '.pyc', 'rb') as pyc:
                pyc_magic = pyc.read(4)
                pyc_ts = struct.unpack('<I', pyc.read(4))[0]
                if pyc_magic == imp.get_magic() and pyc_ts == py_ts:
                    return marshal.load(pyc)
        except:
            pass

        code = self.get_source(fullname)
        compiled_code = compile(code, filename, 'exec')

        try:
            with open(fullname + '.pyc', 'wb') as pyc:
                pyc.write(imp.get_magic())
                pyc.write(struct.pack('<I', py_ts))
                marshal.dump(compiled_code, pyc)
        except:
            pass
        return compiled_code

    def load_module(self, fullname):
        # If the module it's already in there we'll reload but won't remove the
        # entry if we fail
        exists = fullname in sys.modules

        module = types.ModuleType(fullname)
        module.__loader__ = self

        is_package = self.data[fullname][0]
        path = fullname.replace('.', os.path.sep)
        if is_package:
            module.__package__ = fullname
            module.__file__ = os.path.join(path, '__init__.py')
            module.__path__ = [path]
        else:
            module.__package__ = fullname.rsplit('.', 1)[0]
            module.__file__ = path + '.py'

        sys.modules[fullname] = module

        try:
            compiled_code = self.get_code(fullname, module.__file__)
            exec(compiled_code, module.__dict__)
        except:
            if not exists:
                del sys.modules[fullname]
            raise

        return module
''' % {'loader_version': loader_version}

'''
from typing import Optional, Tuple
from base64 import b64encode, b64decode


class Message:
    source_instance_id: str
    destination_instance_id: str
    message_id: str
    reply_message_id: Optional[str]
    purpose: str
    args: Tuple[bytes, ...]

    def __init__(self, source_instance_id: str, destination_instance_id: str, message_id: str, reply_message_id: Optional[str], purpose: str, args: Tuple[bytes, ...]):
        self.source_instance_id = source_instance_id
        self.destination_instance_id = destination_instance_id
        self.message_id = message_id
        self.reply_message_id = reply_message_id
        self.purpose = purpose
        self.args = args

    def to_string(self) -> str:
        return ':'.join([b64encode(prop.encode()).decode() for prop in (
            self.source_instance_id,
            self.destination_instance_id,
            self.message_id,
            self.reply_message_id if self.reply_message_id is not None else '',
            self.purpose,
            ':'.join([b64encode(arg).decode() for arg in self.args])
        )])

    @classmethod
    def from_string(cls, line: str) -> 'Message':
        props = [b64decode(prop).decode() for prop in line.split(':')]
        props_formatted = props[0:3] + [
                props[4] if props[4] != '' else None,
                props[5],
                tuple(b64decode(arg) for arg in props[6].split(':'))
        ]
        return cls(*props_formatted)
if __name__ == '__main__':
    from pyterpreter.run import run
    run()
from pyterpreter.core.message import Message


def run():
    message = Message('', '', '', '', '', ())

    print('Herro der')
'''


inliner_packages = {
    "pyterpreter.core.message": [
        0, 2788, 4246, 1624078685],
    "pyterpreter.core": [
        1, 4246, 4246, 1624097201],
    "pyterpreter": [
        1, 4246, 4319, 1624100749],
    "pyterpreter.run": [
        0, 4319, 4447, 1624100790]
}


def prepare_package():
    # Loader's module name changes with each major version to be able to have
    # different loaders working at the same time.
    module_name = PINLINER_MODULE_NAME + '_' + loader_version.split('.')[0]

    # If the loader code is not already loaded we create a specific module for
    # it.  We need to do it this way so that the functions in there are not
    # compiled with a reference to this module's global dictionary in
    # __globals__.
    module = sys.modules.get(module_name)
    if not module:
        module = types.ModuleType(module_name)
        module.__package__ = ''
        module.__file__ = module_name + '.py'
        exec(inliner_importer_code, module.__dict__)
        sys.modules[module_name] = module

    # We cannot use __file__ directly because on the second run __file__ will
    # be the compiled file (.pyc) and that's not the file we want to read.
    filename = os.path.splitext(__file__)[0] + '.py'

    # Add our own finder and loader for this specific package if it's not
    # already there.
    # This must be done before we initialize the package, as it may import
    # packages and modules contained in the package itself.
    for finder in sys.meta_path:
        if (isinstance(finder, module.InlinerImporter) and
                finder.data == inliner_packages):
            importer = finder
    else:
        # If we haven't forced the setting of the uncaught exception handler
        # we replace it only if it hasn't been replace yet, this is because
        # CPython default handler does not use traceback or even linecache, so
        # it never calls get_source method to get the code, but for example
        # iPython does, so we don't need to replace the handler.
        if FORCE_EXC_HOOK is None:
            set_excepthook = sys.__excepthook__ == sys.excepthook
        else:
            set_excepthook = FORCE_EXC_HOOK

        importer = module.InlinerImporter(inliner_packages, filename,
                                          set_excepthook)
        sys.meta_path.append(importer)

    # If this is a bundle (multiple packages) without default then don't import
    # any package automatically.
    if not PINLINED_DEFAULT_PACKAGE:
        return

    __, start, end, ts = inliner_packages[PINLINED_DEFAULT_PACKAGE]
    with open(filename) as datafile:
        datafile.seek(start)
        code = datafile.read(end - start)

    # We need everything to be local variables before we clear the global dict
    def_package = PINLINED_DEFAULT_PACKAGE
    name = __name__
    filename = def_package + '/__init__.py'
    compiled_code = compile(code, filename, 'exec')

    # Prepare globals to execute __init__ code
    globals().clear()
    # If we've been called directly we cannot set __path__
    if name != '__main__':
        globals()['__path__'] = [def_package]
    else:
        def_package = None
    globals().update(__file__=filename,
                     __package__=def_package,
                     __name__=name,
                     __loader__=importer)

    exec(compiled_code, globals())


# Prepare loader's module and populate this namespace only with package's
# __init__
prepare_package()
