from collections import defaultdict
import subprocess
from tempfile import NamedTemporaryFile as Temp

from . import data


def compare_trees(*trees):
    """Compare trees and yield changed paths."""
    entries = defaultdict(lambda: [None] * len(trees))
    for i, tree in enumerate(trees):
        for path, oid in tree.items():
            entries[path][i] = oid
    
    for path, oids in entries.items():
        yield(path, *oids)


def iter_changed_files(tree1, tree2):
    """Iterate over changed files between two trees."""
    for path, o_from, o_to in compare_trees(tree1, tree2):
        if o_from != o_to:
            action = ('new file' if not o_from else
                      'deleted' if not o_to else
                      'modified')
            yield path, action


def diff_trees(tree1, tree2):
    """Diff two trees and return the output."""
    output = b''
    for path, o_from, o_to in compare_trees(tree1, tree2):
        if o_from != o_to:
            output += diff_blobs(o_from, o_to, path)
    
    return output


def diff_blobs(o_from, o_to, path='blob'):
    """Diff two blobs and return the output."""
    with Temp() as from_file, Temp() as to_file:
        for oid, file in [(o_from, from_file), (o_to, to_file)]:
            if oid:
                file.write(data.get_object(oid))
                file.flush()
        
        with subprocess.Popen(
            ['diff', '--unified', '--show-c-function', '--label', f'a/{path}',  from_file.name, '--label', f'b/{path}', to_file.name],
            stdout=subprocess.PIPE) as proc:
            output, _ = proc.communicate()

        return output


def merge_trees(t_base, t_HEAD, t_other):
    tree = {}
    for path, o_base, o_HEAD, o_other in compare_trees(t_base, t_HEAD, t_other):
        tree[path] = merge_blobs(o_base, o_HEAD, o_other)
    return tree


def merge_blobs(o_base, o_HEAD, o_other):
    with Temp() as f_base, Temp() as f_HEAD, Temp() as f_other:

        #Write blobs to temporary files
        for oid, f in ((o_base, f_base), (o_HEAD, f_HEAD), (o_other, f_other)):
            if oid:
                f.write(data.get_object(oid))
                f.flush()
        
        with subprocess.Popen(
            ['diff3', '-m',
             '-L', 'HEAD', f_HEAD.name,
             '-L', 'BASE', f_base.name,
             '-L', 'MERGE_HEAD', f_other.name],
            stdout=subprocess.PIPE) as proc:
            output, _ = proc.communicate()
            assert proc.returncode in (0,1)

        return output

