#!/usr/bin/env python3

import logging
from setuptools import setup, find_packages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_readme():
    """Read the README file for the long description."""
    try:
        with open('README.md', 'r', encoding='utf-8') as readme_file:
            return readme_file.read()
    except FileNotFoundError:
        logger.error("README.md file not found. Please ensure it exists.")
        return "A simple Git-like version control system"

setup(
    name='agit',
    version='1.0.0',
    author='Aman Kumar',
    author_email='aman.kumar@email.com',
    description='A simple Git-like version control system',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/king04aman/agit',
    packages=['agit'],
    entry_points={
        'console_scripts': [
            'agit = agit.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

logger.info("Setup completed successfully for package: %s", 'agit')
