import argparse
import os
import sys
import textwrap
import subprocess

from . import base
from . import data
from . import diff


def main():
    """Main entry point of the CLI application."""
    args = parse_args()
    args.func(args)


def parse_args():
    """Parse command-line arguments and set up subcommands."""
    parser = argparse.ArgumentParser(description='A simple git clone')

    # Define subcommands
    commands = parser.add_subparsers(title='commands', dest='command')
    commands.required = True

    oid = base.get_oid  # Reference function to get OIDs

    # Command to initialize a new repository
    init_parser = commands.add_parser('init', help='Initialize a new, empty repository')
    init_parser.set_defaults(func=init)

    # Command to store a given blob in the repository
    hash_object_parser = commands.add_parser('hash-object', help='Store a given blob in the repository')
    hash_object_parser.add_argument('file')
    hash_object_parser.set_defaults(func=hash_object)

    # Command to display content of repository objects
    cat_file_parser = commands.add_parser('cat-file', help='Provide content of repository objects')
    cat_file_parser.add_argument('object')
    cat_file_parser.set_defaults(func=cat_file, type=oid)

    # Command to create a tree object from the current directory
    write_tree_parser = commands.add_parser('write-tree', help='Create a tree object from the current directory')
    write_tree_parser.set_defaults(func=write_tree)

    # Command to read a tree object into the current directory
    read_tree_parser = commands.add_parser('read-tree', help='Read a tree object into the current directory')
    read_tree_parser.add_argument('tree', type=oid)
    read_tree_parser.set_defaults(func=read_tree)

    # Command to record changes to the repository
    commit_parser = commands.add_parser('commit', help='Record changes to the repository')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')
    commit_parser.set_defaults(func=commit)

    # Command to show the history of the repository
    log_parser = commands.add_parser('log', help='Show history of the repository')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', default='@', type=oid, nargs='?')

    # Command to show the diff content of a repository commit object
    show_parser = commands.add_parser('show', help='Show the diff content of a repository commit object')
    show_parser.add_argument('oid', default='@', type=oid, nargs='?')
    show_parser.set_defaults(func=show)

    # Command to show the diff content of a repository commit object    
    diff_parser = commands.add_parser('diff', help='Show the diff content of a repository commit object')
    diff_parser.add_argument('commit', default='@', type=oid, nargs='?')
    diff_parser.set_defaults(func=_diff)

    # Command to checkout a commit by its object ID
    checkout_parser = commands.add_parser('checkout', help='Checkout a commit inside the current directory')
    checkout_parser.add_argument('commit')
    checkout_parser.set_defaults(func=checkout)

    # Command to create a tag reference
    tag_parser = commands.add_parser('tag', help='Create a tag reference')
    tag_parser.add_argument('name')
    tag_parser.add_argument('oid', default='@', type=oid, nargs='?')
    tag_parser.set_defaults(func=create_tag)

    # Command for visualization (k command)
    k_parser = commands.add_parser('k', help='k command visualization')
    k_parser.set_defaults(func=k)

    # Command to create a new branch
    branch_parser = commands.add_parser('branch', help='Create a new branch')
    branch_parser.add_argument('name', nargs='?')
    branch_parser.add_argument('start_point', default='@', type=oid, nargs='?')
    branch_parser.set_defaults(func=branch)
    
    # Command to show the working tree status
    status_parser = commands.add_parser('status', help='Show the working tree status')
    status_parser.set_defaults(func=status)

    # Command to reset the current HEAD to the specified object ID  (Commit)
    reset_parser = commands.add_parser('reset', help='Reset the current HEAD to the specified object ID (Commit)')
    reset_parser.add_argument('commit', type=oid)
    reset_parser.set_defaults(func=reset)


    return parser.parse_args()


def init(args):
    """Initialize a new repository and create the necessary directories."""
    base.init()
    print(f'Initialized empty agit repository in {os.getcwd()}/{data.GIT_DIR}')


def hash_object(args):
    """Hash a file and print its object ID."""
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    """Print the content of the specified object."""
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))


def write_tree(args):
    """Create and print the object ID of the tree representing the current directory."""
    print(base.write_tree())


def read_tree(args):
    """Read a specified tree object into the current directory."""
    base.read_tree(args.tree)


def commit(args):
    """Create a commit with the provided message and print its object ID."""
    print(base.commit(args.message))


def _print_commit(oid, commit_data, refs=None):
    """Print the commit data."""
    refs_str = f' ({", ".join(refs)})' if refs else ''
    print(f'commit {oid}{refs_str}\n')
    print(textwrap.indent(commit_data.message, '    '))
    print('')
    

def log(args):
    """Display the commit history starting from the specified object ID."""
    refs = {}
    for refname, ref in data.iter_refs():
        refs.setdefault(ref.value, []).append(refname)

    for oid in base.iter_commits_and_parents({args.oid}):
        commit_data = base.get_commit(oid)
        _print_commit(oid, commit_data, refs.get(oid))


def show(args):
    """Show the diff content of a commit object."""
    if not args.oid:
        return
    commit = base.get_commit(args.oid)
    parent_tree = None
    if commit.parent:
        parent_tree = base.get_commit(commit.parent).tree

    _print_commit(args.oid, commit)
    result = diff.diff_trees(base.get_tree(parent_tree), base.get_tree(commit.tree))
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def _diff(args):
    tree = args.commit and base.get_commit(args.commit).tree

    result = diff.diff_trees(base.get_tree(tree), base.get_working_tree())
    sys.stdout.flush()
    sys.stdout.buffer.write(result)


def checkout(args):
    """Checkout the specified commit by its object ID."""
    base.checkout(args.commit)


def create_tag(args):
    """Create a tag with the specified name and optional object ID."""
    base.create_tag(args.name, args.oid)


def k(args):
    """Generate a visualization of commits in DOT format."""
    dot = 'digraph commits {\n'

    oids = set()
    for refname, ref in data.iter_refs(deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            oids.add(ref.value)
    
    for oid in base.iter_commits_and_parents(oids):
        commit_data = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        if commit_data.parent:
            dot += f'"{oid}" -> "{commit_data.parent}"\n'
    
    dot += '}'
    print(dot)

    # Visualize the graph using Graphviz
    with subprocess.Popen(['dot', '-Tgtk', '/dev/stdin'], stdin=subprocess.PIPE) as proc:
        proc.communicate(dot.encode())


def branch(args):
    """Create a new branch with the specified name and optional start point."""
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = '*' if branch == current else ' '
            print(f'{prefix} {branch}')
    else:
        base.create_branch(args.name, args.start_point)
        print(f'Branch {args.name} created at {args.start_point[:10]}')


def reset(args):
    """Reset the current HEAD to the specified object ID."""
    base.reset(args.commit)


def status(args):
    HEAD = base.get_oid('@')
    branch = base.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')

    print('\nChanges to be committed:\n')
    HEAD_tree = HEAD and base.get_commit(HEAD).tree
    for path, action in diff.iter_changed_files(base.get_tree(HEAD_tree), base.get_working_tree()):
        print(f'    {action:>12}: {path}')



if __name__ == '__main__':
    main()
