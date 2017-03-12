import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit

def sys_python_install_common(py_version='3.5'):
    """ Install common python application - Ex: (cmd) """

    major = py_version.split('.')[0]
    if major == '2':
        major = ''
    requirements = '%s' % ' '.join([
        'python{}-dev'.format(major),
        'python{}-setuptools'.format(major),
        'python{}-psycopg2'.format(major),
        # 'python{}-imaging'.format(major),
        'python{}-pip'.format(major),
        'python{}-pil'.format(major),

        # 'virtualenvwrapper',
        'python-dev',
        'python-virtualenv',
        'libfreetype6-dev',
        'libjpeg62-dev',
        'libpng12-dev',
        'zlib1g-dev',
        'liblcms2-dev',
        'libwebp-dev',
        'tcl8.5-dev',
        'tk8.5-dev',
    ])
    sudo('apt -y install {}'.format(requirements))
    if major == '2':
        sudo('pip install pillow')
    else:
        sudo('pip3 install pillow')
    sys_etc_git_commit('Installed common python packages')



