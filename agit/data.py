import os
import hashlib

from collections import namedtuple


GIT_DIR = '.agit'
RefValue = namedtuple('RefValue', ['symbolic', 'value'])


def init():
    """Initialize a new Git-like repository structure."""
    os.makedirs(os.path.join(GIT_DIR, 'objects'), exist_ok=True)
    os.makedirs(os.path.join(GIT_DIR, 'refs'), exist_ok=True)


def update_ref(ref, value):
    """Update a reference with the given object ID."""
    assert not value.symbolic
    ref = _get_ref_internal(ref)[0]
    ref_path = os.path.join(GIT_DIR, ref)
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(value.value)


def get_ref(ref):
    """Retrieve the object ID associated with a given reference."""
    return _get_ref_internal(ref)[1]


def _get_ref_internal(ref):
    """Retrieve the object ID associated with a given reference."""
    ref_path = os.path.join(GIT_DIR, ref)
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()
    
    symbolic = bool(value) and value.startswith('ref:')
    if symbolic:
        value = value.split(':', 1)[1].strip()
        return _get_ref_internal(value)
    
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


def iter_refs():
    """Iterate over references in the repository."""
    refs = ['HEAD']
    refs_dir = os.path.join(GIT_DIR, 'refs')
    
    for root, _, filenames in os.walk(refs_dir):
        for name in filenames:
            ref_path = os.path.relpath(os.path.join(root, name), GIT_DIR)
            refs.append(ref_path)
    
    for ref in refs:
        yield ref, get_ref(ref)
