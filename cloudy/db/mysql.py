import os
import re
import sys
from operator import itemgetter
import datetime

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files

from cloudy.sys.etc import sys_etc_git_commit


def db_mysql_latest_version():
    """ Get the latest available mysql version - Ex: (cmd)"""

    latest_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('apt-cache search --names-only mysql-client')

    version_re = re.compile('mysql-client-([0-9.]*)\s-')
    lines = ret.split('\n')
    versions = []
    for line in lines:
        ver = version_re.search(line.lower())
        if ver:
            versions.append(ver.group(1))

    versions.sort(key = itemgetter(2), reverse = True)
    try:
        latest_version = versions[0]
    except:
        pass

    print >> sys.stderr, 'Latest available mysql is: [{}]'.format(latest_version)
    return latest_version


def db_mysql_server_install(version=''):
    """ Install MySQL Server - Ex: (cmd:[5.7])"""

    if not version:
        version = db_mysql_latest_version()

    # requirements
    requirements = '%s' % ' '.join([
        'mysql-server-{}'.format(version),
    ])

    # install requirements
    sudo('DEBIAN_FRONTEND=noninteractive; apt-get -y install {}'.format(requirements))
    sys_etc_git_commit('Installed MySQL Server ({})'.format(version))


def db_mysql_client_install(version=''):
    """ Install MySQL Client - Ex: (cmd:[5.7])"""

    if not version:
        version = db_mysql_latest_version()

    # requirements
    requirements = '%s' % ' '.join([
        'mysql-client-{}'.format(version),
    ])

    # install requirements
    sudo('DEBIAN_FRONTEND=noninteractive; apt-get -y install {}'.format(requirements))
    sys_etc_git_commit('Installed MySQL Client ({})'.format(version))


def db_mysql_set_root_password(password):
    """ Set MySQL Root Password - Ex: (cmd:<mypass>)"""
    if not password:
        print >> sys.stderr, 'Password required for mysql root'
    else:
        run('mysqladmin -u root password {}'.format(password))
        sys_etc_git_commit('Set MySQL Root Password')

