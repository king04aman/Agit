import argparse
import os
import sys
import textwrap
import subprocess

from . import base
from . import data


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser(description='A simple git clone')

    commands = parser.add_subparsers(title='commands', dest='command')
    commands.required = True

    oid = base.get_oid

    init_parser = commands.add_parser('init', help='Initialize a new, empty repository')
    init_parser.set_defaults(func=init)

    hash_object_parser = commands.add_parser('hash-object', help='Store a given blob in the repository')
    hash_object_parser.add_argument('file')
    hash_object_parser.set_defaults(func=hash_object)

    cat_file_parser = commands.add_parser('cat-file', help='Provide content of repository objects')
    cat_file_parser.add_argument('object')
    cat_file_parser.set_defaults(func=cat_file, type=oid)

    write_tree_parser = commands.add_parser('write-tree', help='Create a tree object from the current directory')
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser('read-tree', help='Read a tree object into the current directory')
    read_tree_parser.add_argument('tree', type=oid)
    read_tree_parser.set_defaults(func=read_tree)
    
    commit_parser = commands.add_parser('commit', help='Record changes to the repository')
    commit_parser.add_argument('-m', '--message', required=True, help='Commit message')
    commit_parser.set_defaults(func=commit)

    log_parser = commands.add_parser('log', help='Show history of the repository')
    log_parser.set_defaults(func=log)
    log_parser.add_argument('oid', default='@', type=oid, nargs='?')

    checkout_parser = commands.add_parser('checkout', help='Checkout a commit inside the current directory')
    checkout_parser.add_argument('oid', type=oid)
    checkout_parser.set_defaults(func=checkout)

    tag_parser = commands.add_parser('tag', help='Create a tag reference')
    tag_parser.add_argument('name')
    tag_parser.add_argument('oid', default='@', type=oid, nargs='?')
    tag_parser.set_defaults(func=create_tag)

    k_parser = commands.add_parser('k', help='k command visualization')
    k_parser.set_defaults(func=k)

    return parser.parse_args()


def init(args):
    data.init()
    print(f'Initialized empty agit repository in {os.getcwd()}/{data.GIT_DIR}')


def hash_object(args):
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))


def cat_file(args):
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))


def write_tree(args):
    print(base.write_tree())


def read_tree(args):
    base.read_tree(args.tree)


def commit(args):
    print(base.commit(args.message))


def log(args):
    oid = args.oid
    while oid:
        commit = base.get_commit(oid)
        print(f'commit {oid}\n')
        print(textwrap.indent(commit.message, '    '))
        print('')
        oid = commit.parent


def checkout(args):
    base.checkout(args.oid)


def create_tag(args):
    base.create_tag(args.name, args.oid)


def k(args):
    dot = 'digraph commits {\n'

    oids = set()
    for refname, ref in data.iter_refs():
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref}"\n'
        oids.add(ref)
    
    for oid in base.iter_commits_and_parents(oids):
        commit = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        if commit.parent:
            dot += f'"{oid}" -> "{commit.parent}"\n'
    
    dot += '}'
    print(dot)

    #TODO visualize the refs
    with subprocess.Popen(['dot', '-Tgtk', '/dev/stdin'], stdin=subprocess.PIPE) as proc:
        proc.communicate(dot.encode())


if __name__ == '__main__':
    main()

