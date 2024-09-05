import os

from . import data

def write_tree(directory='.'):
    with os.scandir(directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}'
            if is_ignored(full):
                continue

            if entry.is_file(follow_symlinks=False):
                with open(full, 'rb') as f:
                    print(data.hash_object(f.read()))
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

    # TODO write the tree object

def is_ignored(path):
    return '.agit' in path.split('/')
