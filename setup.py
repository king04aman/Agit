#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='agit',
    version='1.0.0',
    author='Aman Kumar',
    author_email='aman.kumar@email.com',
    description='A simple Git-like version control system',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/king04aman/agit',
    packages=find_packages(where='agit'),
    package_dir={'': 'agit'},
    entry_points={
        'console_scripts': [
            'agit = cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

