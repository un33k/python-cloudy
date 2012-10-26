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

from cloudy.sys.etc import sys_etc_git_commit

def sys_python_install_common():
    """ Install common python application - Ex: (cmd) """

    requirements = '%s' % ' '.join([
        'python-psycopg2',
        'python-setuptools',
        'python-dev',
        'python-virtualenv',
    ])
    sudo('apt-get -y install {0}'.format(requirements))
    sys_etc_git_commit('Installed common python packages')



