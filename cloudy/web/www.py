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

def web_install_common():
    """ Install common web server/proxy packages - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'nginx',
        'supervisor',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    sys_etc_git_commit('Installed web server/proxy system packages')


def web_create_data_directory(web_dir='/srv/www'):
    """ Create a data directory for the web files """
    sudo('mkdir -p {0}'.format(web_dir))


def web_create_site_directory(domain):
    """ Create a site directory - Ex: (cmd:<domain>)"""
    path = '/srv/www/{0}'.format(domain)
    sudo('mkdir -p %s/{pri,pub,log,bck}' % path)
    sudo('chown -R :www-data {0}'.format(path))
    sudo('chmod -R g+w {0}/pub'.format(path))
    sudo('chmod -R g+w {0}/log'.format(path))



