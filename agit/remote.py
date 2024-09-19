import os
from . import data


REMOTE_REFS_BASE = 'refs/heads'
LOCAL_REFS_BASE = 'refs/remotes'


def fetch(remote_path):
    """Fetch objects and refs from a remote repository."""
    # Get the refs from the remote repository
    refs = _get_remote_refs(remote_path, REMOTE_REFS_BASE)

    # Update the local refs
    for remote_name, value in refs.items():
        refname = os.path.relpath(remote_name, REMOTE_REFS_BASE)
        data.update_ref(f'{LOCAL_REFS_BASE}/{refname}', data.RefValue(symbolic=False, value=value))


def _get_remote_refs(remote_path, prefix=''):
    """Retrieve refs from a remote repository."""
    with data.change_git_dir(remote_path):
        return {refname: ref.value for refname, ref in data.iter_refs(prefix)}


