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


def web_create_virtual_env(domain):
    """ Create a virtual env for a domain - Ex: (cmd:foo.example.com)"""
    path = '/srv/www/{0}/pri'.format(domain)
    with cd(path):
        sudo('virtualenv --no-site-packages venv')


def web_install_python_image_library(domain, py_version=''):
    """ Install PIL into a domain directory """
    if not py_version:
        with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            py_version = run("ls -la /usr/bin/python | head -n 1 | awk '{print $11}'")

    if not py_version:
        fail('Failed to find python version')
    
    site_packages = '/srv/www/{0}/pri/venv/lib/{1}/site-packages'.format(domain, py_version)
    dist_packages = '/usr/lib/{0}/dist-packages'.format(py_version)
    with cd(site_packages):
        sudo('ln -sf {0}/PIL'.format(dist_packages))
        sudo('ln -sf {0}/PIL.pth'.format(dist_packages))



