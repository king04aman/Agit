from collections import defaultdict


def compare_trees(*trees):
    """Compare trees and yield changed paths."""
    entries = defaultdict(lambda: [None] * len(trees))
    for i, tree in enumerate(trees):
        for path, oid in tree.items():
            entries[path][i] = oid
    
    for path, oids in entries.items():
        yield(path, *oids)


def diff_trees(tree1, tree2):
    """Diff two trees and return the output."""
    output = ''
    for path, oid1, oid2 in compare_trees(tree1, tree2):
        if oid1 != oid2:
            output += (f'blob {oid1} {oid2} {path}')
    
    return output
