#!/usr/bin/env python

from setuptools import setup
import re
import os
import sys

name = 'python-cloudy'
package = 'cloudy'
description = 'A Python utility that simplifies cloud configuration'
url = 'https://github.com/un33k/python-cloudy'
author = 'Val Neekman'
author_email = 'info@neekware.com'
license = 'BSD'
install_requires = [
    'fabric>=2.7',
    'apache-libcloud>=3.6.1',
    's3cmd>=2.3.0'
]
classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: POSIX',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8') as f:
        return f.read()

def get_version(package):
    """
    Return package version as listed in `__version__` in `__init__.py`.
    """
    init_py = open(os.path.join(package, '__init__.py'), encoding='utf-8').read()
    return re.search(r"^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)

def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]

def get_package_data(package):
    """
    Return all files under the root package, that are not in a package themselves.
    """
    walk = [
        (dirpath.replace(package + os.sep, '', 1), filenames)
        for dirpath, dirnames, filenames in os.walk(package)
        if not os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]
    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename) for filename in filenames])
    return {package: filepaths}

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version(package)}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()

setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires,
    classifiers=classifiers,
    python_requires='>=3.7',
)


