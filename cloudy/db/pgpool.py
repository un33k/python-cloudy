import os
import re
import sys
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


def db_pgpool2_install():
    """ Install pgpool2 - Ex: (cmd:)"""

    # requirements
    requirements = '%s' % ' '.join([
        'pgpool2',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    sys_etc_git_commit('Installed pgpool2')


def db_pgpool2_configure(dbhost=''):
    """ Install pgpool2 - Ex: (cmd:)"""
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'pgpool2/pgpool.conf'))
    remotecfg = '/etc/pgpool2/pgpool.conf'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    if dbhost:
        sudo('sed -i "s/dbhost/{0}/g" {1}'.format(dbhost, remotecfg))

    localdefault = os.path.expanduser(os.path.join(cfgdir, 'pgpool2/default-pgpool2'))
    remotedefault = '/etc/default/pgpool2'
    sudo('rm -rf ' + remotedefault)
    put(localdefault, remotedefault, use_sudo=True)

    sys_etc_git_commit('Configured pgpool2')






