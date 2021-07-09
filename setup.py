# -*- coding: utf-8 -*-

import os
from setuptools import find_packages

about = {}
with open(os.path.join('ExtractTable', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open('README.md', 'r') as f:
    readme = f.read()

with open("requirements.txt") as fh:
    requires = [x.strip() for x in fh.readlines()]


def setup_package():
    metadata = dict(
        name=about['__title__'],
        version=about['__version__'],
        description=about['__description__'],
        long_description=readme,
        long_description_content_type="text/markdown",
        url=about['__url__'],
        author=about['__author__'],
        author_email=about['__author_email__'],
        license=about['__license__'],
        packages=find_packages(),
        install_requires=requires,
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10'
        ])

    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

    setup(**metadata)


if __name__ == '__main__':
    setup_package()
