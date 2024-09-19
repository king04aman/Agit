from . import data


def fetch(remote_path):
    """Fetch objects and refs from a remote repository."""
    print("Will fetch the following refs:")
    with data.change_git_dir(remote_path):
        for refname, _ in data.iter_refs('refs/heads'):
            print(f'- {refname}')
            data.update_ref(refname, data.get_ref(refname))

