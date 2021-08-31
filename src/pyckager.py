import sys
from base64 import b64encode
import os
from typing import Dict, Tuple, List

packages_source_dict: Dict[str, Tuple[bool, str]] = {}


def is_module(path: str):
    # This validation is poor, but good enough for now
    return os.path.isfile(path) and path.endswith('.py')


def is_package(path: str):
    init_file = os.path.join(path, '__init__.py')
    return os.path.isdir(path) and os.path.isfile(init_file)


def process_directory(base_dir, package_path):
    files = []
    contents = os.listdir(os.path.join(base_dir, package_path))
    for content in contents:  # type: str
        next_path = os.path.join(package_path, content)
        path = os.path.join(base_dir, next_path)
        if is_module(path):
            files.append(process_file(base_dir, next_path))
        elif is_package(path):
            files.extend(process_directory(base_dir, next_path))
    return files


def process_file(base_dir: str, package_path: str):
    path = os.path.splitext(package_path)[0].replace(os.path.sep, '.')
    full_path = os.path.join(base_dir, package_path)
    is_package_init = path.endswith('__init__')
    if is_package_init:
        path = path[:-len('/__init__')]  # remove '/__init__' from the end of the path

    with open(full_path, 'r') as f:
        code = f.read()
        packages_source_dict[path] = (is_package_init, code)


def process_packages(package_paths: List[str], log=False) -> str:
    default_package = os.path.split(package_paths[0])[1]  # default package is the first package
    for package_path in package_paths:
        base_dir, module_name = os.path.split(package_path)
        process_directory(base_dir, module_name)

    packages_encoded_lines = []
    for package_name, (is_package_init, package_source) in packages_source_dict.items():
        if log:
            print(f'Processing {package_name} ({len(package_source)})')
        packages_encoded_lines.append(f"        '{package_name}': ({is_package_init}, '{b64encode(package_source.encode()).decode()}'),")
    packages_encoded_str = '\n'.join(packages_encoded_lines)

    with open('pyckager_template.py') as fh:
        template = fh.read()

    template = template.replace('<DEFAULT_PACKAGE_NAME_INSERTED_HERE>', default_package)
    template = template.replace('        # <PACKAGES_INSERTED_HERE>', packages_encoded_str)
    return template


def main():
    package_paths = sys.argv[1:]
    if len(package_paths) == 0:
        print('Please specify package paths: eg "pyckager src/package1 src/package2"\nWith the package to be imported automatically first')
        exit(-1)
    output = process_packages(package_paths, True)

    with open('pyckager_out.py', 'w') as fh:
        fh.write(output)


if __name__ == '__main__':
    main()

