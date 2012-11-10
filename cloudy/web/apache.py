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
from fabric.api import cd
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit

def web_apache_install():
    """ Install apache2  - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'apache2',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    util_apache2_bootstrap()
    sys_etc_git_commit('Installed apache2')


def util_apache2_bootstrap():
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/ports.conf'))
    remotecfg = '/etc/apache2/ports.conf'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sudo('rm -f /etc/apache2/sites-enabled/*default*')
    files.append('/etc/apache2/envvars', ['export LANG="en_US.UTF-8"', 'export LC_ALL="en_US.UTF-8"'], use_sudo=True)


def web_install_apache_mods():
    """ Install apache2 related packages - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'libapache2-mod-wsgi',
        'libapache2-mod-rpaf',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    with settings(warn_only=True):
        sudo('a2enmod wsgi')
        sudo('a2enmod rpaf')
    sys_etc_git_commit('Installed apache2 and related packages')



