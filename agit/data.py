import os
import hashlib

from collections import namedtuple
from contextlib import contextmanager


# Will be initialized by the `cli.main()` function
GIT_DIR = None
RefValue = namedtuple('RefValue', ['symbolic', 'value'])


@contextmanager
def change_git_dir(new_dir):
    """Change the GIT_DIR context for the duration of the context manager."""
    global GIT_DIR
    old_dir, GIT_DIR = GIT_DIR, f'{new_dir}/.agit'
    yield
    GIT_DIR = old_dir


def init():
    """Initialize a new Git-like repository structure."""
    os.makedirs(os.path.join(GIT_DIR, 'objects'), exist_ok=True)
    os.makedirs(os.path.join(GIT_DIR, 'refs'), exist_ok=True)


def update_ref(ref, value, deref=True):
    """Update a reference with the given object ID."""
    ref = _get_ref_internal(ref, deref)[0]

    assert value.value
    if value.symbolic:
        value = f'ref: {value.value}'
    else:
        value = value.value

    ref_path = os.path.join(GIT_DIR, ref)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(value)


def get_ref(ref, deref=True):
    """Retrieve the object ID associated with a given reference."""
    return _get_ref_internal(ref)[1]


def delete_ref(ref, deref=True):
    """Delete a reference."""
    ref = _get_ref_internal(ref, deref)[0]
    os.remove(os.path.join(GIT_DIR, ref))
    

def _get_ref_internal(ref, deref):
    """Retrieve the object ID associated with a given reference."""
    ref_path = os.path.join(GIT_DIR, ref)
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()
    
    symbolic = bool(value) and value.startswith('ref:')
    if symbolic:
        value = value.split(':', 1)[1].strip()
        if deref:
            return _get_ref_internal(value, deref=True)
    
    return ref, RefValue(symbolic=False, value=value)


def hash_object(data, type_='blob'):
    """Hash the given data and store it in the objects directory."""
    obj = f"{type_}\x00".encode() + data
    oid = hashlib.sha1(obj).hexdigest()
    object_path = os.path.join(GIT_DIR, 'objects', oid)
    with open(object_path, 'wb') as out:
        out.write(obj)
    return oid


def get_object(oid, expected='blob'):
    """Retrieve the content of an object by its object ID."""
    object_path = os.path.join(GIT_DIR, 'objects', oid)
    with open(object_path, 'rb') as f:
        obj = f.read()
    
    type_, _, content = obj.partition(b'\x00')
    type_ = type_.decode()

    if expected is not None:
        assert type_ == expected, f'Expected {expected}, got {type_}'
    
    return content


def iter_refs(prefix='', deref=True):
    """Iterate over references in the repository."""
    refs = ['HEAD', 'MERGE_HEAD']
    refs_dir = os.path.join(GIT_DIR, 'refs')
    
    for root, _, filenames in os.walk(refs_dir):
        for name in filenames:
            ref_path = os.path.relpath(os.path.join(root, name), GIT_DIR)
            refs.append(ref_path)
    
    for refname in refs:
        if not refname.startswith(prefix):
            continue
        ref = get_ref(refname, deref=deref)
        if ref.value:
            yield refname, ref
        
