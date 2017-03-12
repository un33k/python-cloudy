import os
import re
import sys
import time
from operator import itemgetter

from fabric.api import local
from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files

from cloudy.db.psql import db_psql_default_installed_version
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_restart_service


def db_pgpool2_install():
    """ Install pgpool2 - Ex: (cmd:)"""

    # requirements
    requirements = '%s' % ' '.join([
        'pgpool2',
    ])

    # install requirements
    sudo('apt -y install {}'.format(requirements))
    sys_etc_git_commit('Installed pgpool2')


def db_pgpool2_configure(dbhost='', dbport=5432, localport=5432):
    """ Install pgpool2 - Ex: (cmd:)"""
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'pgpool2/pgpool.conf'))
    remotecfg = '/etc/pgpool2/pgpool.conf'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sudo('sed -i "s/dbhost/{}/g" {}'.format(dbhost, remotecfg))
    sudo('sed -i "s/dbport/{}/g" {}'.format(dbport, remotecfg))
    sudo('sed -i "s/localport/{}/g" {}'.format(localport, remotecfg))

    localdefault = os.path.expanduser(os.path.join(cfgdir, 'pgpool2/default-pgpool2'))
    remotedefault = '/etc/default/pgpool2'
    sudo('rm -rf ' + remotedefault)
    put(localdefault, remotedefault, use_sudo=True)
    sys_etc_git_commit('Configured pgpool2')
    sys_restart_service('pgpool2')





