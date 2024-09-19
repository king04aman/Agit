from . import data


def fetch(remote_path):
    """Fetch objects and refs from a remote repository."""
    print("Will fetch the following refs:")
    for refname, _ in _get_remote_refs(remote_path, 'refs/heads').items():
        print(f'- {refname}')


def _get_remote_refs(remote_path, prefix=''):
    """Retrieve refs from a remote repository."""
    with data.change_git_dir(remote_path):
        return {refname: ref.value for refname, ref in data.iter_refs(prefix)}


