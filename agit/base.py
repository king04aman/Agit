import os
import itertools
import operator
import string
from collections import deque, namedtuple

from . import data
from . import diff


def init():
    data.init()
    data.update_ref('HEAD', data.RefValue(symbolic=True, value='refs/heads/master'))


def write_tree(directory='.'):
    """Write the current directory's state to a tree object."""
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            full_path = os.path.join(directory, entry.name)
            if is_ignored(full_path):
                continue

            if entry.is_file(follow_symlinks=False):
                type_ = 'blob'
                with open(full_path, 'rb') as f:
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = 'tree'
                oid = write_tree(full_path)
            entries.append((entry.name, oid, type_))

        tree = ''.join(f'{type_} {oid} {name}\n' for name, oid, type_ in sorted(entries))
        return data.hash_object(tree.encode(), 'tree')


def _iter_tree_entries(oid):
    """Yield entries from a tree object."""
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split()
        yield type_, oid, name


def get_tree(oid, base_path=''):
    """Retrieve the full tree structure for a given object ID."""
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert '/' not in name
        assert name not in ('.', '..')
        path = os.path.join(base_path, name)
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update(get_tree(oid, f'{path}/'))
        else:
            raise ValueError(f'Unknown tree entry {type_}')
    return result


def get_working_tree():
    """Retrieve the current working tree."""
    result = {}
    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename))
            if is_ignored(path) or not os.path.isfile(path):
                continue
            with open(path, 'rb') as f:
                result[path] = data.hash_object(f.read())

    return result


def _empty_current_directory():
    """Remove all files and directories from the current directory."""
    for root, dirnames, filenames in os.walk('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename))
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        for dirname in dirnames:
            path = os.path.relpath(os.path.join(root, dirname))
            if is_ignored(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                # Deletion might fail if the directory is not empty
                pass


def read_tree(tree_oid):
    """Read the tree object into the current directory."""
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path='./').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data.get_object(oid))


def commit(message):
    """Create a commit with the given message."""
    commit_data = f'tree {write_tree()}\n'

    HEAD = data.get_ref('HEAD').value
    if HEAD:
        commit_data += f'parent {HEAD}\n'

    MERGE_HEAD = data.get_ref('MERGE_HEAD').value
    if MERGE_HEAD:
        commit_data += f'parent {MERGE_HEAD}\n'
        data.delete_ref('MERGE_HEAD', deref=False)

    commit_data += '\n' + message + '\n'
    oid = data.hash_object(commit_data.encode(), 'commit')
    data.update_ref('HEAD', data.RefValue(symbolic=False, value=oid))
    return oid


def checkout(name):
    """Checkout a specific commit by its object ID."""
    oid = get_oid(name)
    commit_data = get_commit(oid)
    read_tree(commit_data.tree)

    if is_branch(name):
        HEAD = data.RefValue(symbolic=True, value=f'refs/heads/{name}')
    else:
        HEAD = data.RefValue(symbolic=False, value=oid)
    
    data.update_ref('HEAD', HEAD, deref=False)


def reset(oid):
    """Reset the current HEAD to the specified object ID."""
    data.update_ref('HEAD', data.RefValue(symbolic=False, value=oid))


def read_tree_merged(t_HEAD, t_other):
    """Read the tree object into the current directory."""
    _empty_current_directory()
    for path, blob in diff.merge_trees(get_tree(t_HEAD), get_tree(t_other)).items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(blob)


def merge(other):
    """Merge the specified branch into the current one."""
    HEAD = data.get_ref('HEAD').value
    assert HEAD
    c_HEAD = get_commit(HEAD)
    c_other = get_commit(other)

    data.update_ref('MERGE_HEAD', data.RefValue(symbolic=False, value=other))
    read_tree_merged(c_HEAD.tree, c_other.tree)
    print('Merged in working directory. Use "agit commit" to conclude merge.')


def create_tag(name, oid):
    """Create a tag (to be implemented)."""
    data.update_ref (f'refs/tags/{name}', data.RefValue (symbolic=False, value=oid))


def create_branch(name, oid):
    """Create a branch with the given name and object ID."""
    data.update_ref(f'refs/heads/{name}', data.RefValue(symbolic=False, value=oid))


Commit = namedtuple('Commit', ['tree', 'parents', 'message'])


def get_commit(oid):
    """Retrieve a commit object by its ID."""
    parents = []
    commit = data.get_object(oid, 'commit').decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile(operator.truth, lines):
        key, value = line.split(' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parents.append(value)
        else:
            raise ValueError(f'Unknown field {key}')

    message = '\n'.join(lines)
    return Commit(tree=tree, parents=parents, message=message)


def iter_commits_and_parents(oids):
    """Iterate through a set of commits and their parents."""
    oids = deque(set(oids))
    visited = set()

    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add(oid)
        yield oid

        commit = get_commit(oid)
        # Return first parent first, so it is processed first
        oids.extendleft(commit.parents[:1])
        # Return other parents in reverse order, so they are processed last
        oids.extend(commit.parents[1:])


def get_oid(name):
    """Retrieve the object ID from a name or reference."""
    if name == '@':
        name = 'HEAD'

    refs_to_try = [
        f'{name}',
        f'refs/{name}',
        f'refs/tags/{name}',
        f'refs/heads/{name}',
    ]

    for ref in refs_to_try:
        if data.get_ref(ref, deref=False).value:
            return data.get_ref(ref).value

    is_hex = all(c in string.hexdigits for c in name)
    if len(name) == 40 and is_hex:
        return name

    raise ValueError(f'Unknown name {name}')


def iter_branch_names():
    """Iterate over all branch names."""
    for refname, _ in data.iter_refs('refs/heads'):
        yield os.path.relpath(refname, 'refs/heads/')
        

def get_branch_name():
    HEAD = data.get_ref('HEAD', deref=False)
    if not HEAD.symbolic:
        return None

    HEAD = HEAD.value
    assert HEAD.startswith('refs/heads/')
    return os.path.relpath(HEAD, 'refs/heads/')


def is_ignored(path):
    """Determine if a file or directory should be ignored."""
    return '.agit' in path.split('/')


def is_branch(branch):
    """Determine if a branch exists."""
    return data.get_ref(f'refs/heads/{branch}').value is not None