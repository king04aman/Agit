 #!/usr/bin/env python3

from setuptools import setup

setup (name = 'agit',
        version = '1.0',
        packages = ['agit'],
        entry_points = {
            'console_scripts' : [
                'agit = agit.cli:main'
            ]
        })

