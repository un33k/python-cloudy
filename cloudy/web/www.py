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
from fabric.api import prefix
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit


def web_create_data_directory(web_dir='/srv/www'):
    """ Create a data directory for the web files """
    sudo('mkdir -p {}'.format(web_dir))


def web_create_shared_directory(shared_dir='/srv/www/shared'):
    """ Create a site directory - Ex: (cmd:<shared_dir>)"""
    sudo('mkdir -p {}'.format(shared_dir))
    sudo('chown -R :www-data {}'.format(shared_dir))
    sudo('chmod -R g+wrx {}'.format(shared_dir))


def web_create_seekrets_directory(seekrets_dir='/srv/www/seekrets'):
    """ Create a seekrets directory - Ex: (cmd:<seekrets_dir>)"""
    sudo('mkdir -p {}'.format(seekrets_dir))
    sudo('chown -R :www-data {}'.format(seekrets_dir))
    sudo('chmod -R g+wrx {}'.format(seekrets_dir))


def web_create_site_directory(domain):
    """ Create a site directory - Ex: (cmd:<domain>)"""
    path = '/srv/www/{}'.format(domain)
    sudo('mkdir -p %s/{pri,pub,log,bck}' % path)
    sudo('chown -R :www-data {}'.format(path))
    sudo('chmod -R g+w {}/pub'.format(path))
    sudo('chmod -R g+w {}/log'.format(path))


def web_create_virtual_env(domain, py_version='2.7'):
    """ Create a virtual env for a domain - Ex: (cmd:foo.example.com)"""
    path = '/srv/www/{}/pri'.format(domain)
    with cd(path):
        py_major = py_version.split('.')[0]
        sudo('virtualenv -p python{} --always-copy --no-site-packages --distribute venv'.format(py_version))
        sudo('chown -R :www-data venv')
        sudo('chmod -R g+wrx venv')

def web_create_site_log_file(domain):
    """ Create a log file with proper permissions for Django """
    site_logfile = '/srv/www/{}/log/{}.log'.format(domain, domain)
    sudo('touch {}'.format(site_logfile))
    sudo('chown :www-data {}'.format(site_logfile))
    sudo('chmod g+rw {}'.format(site_logfile))

def web_prepare_site(domain, py_version='2'):
    """ Create a site directory and everything else for the site on production server """

    web_create_site_directory(domain)
    web_create_virtual_env(domain, py_version)
    web_create_site_log_file(domain)

def web_deploy(domain):
    """ Push changes to a production server """

    webroot = '/srv/www/{}/pri/venv/webroot'.format(domain)
    with cd(webroot):
        with prefix('source {}/../bin/activate'.format(webroot)):
            run('git pull')
            run('pip install -r env/deploy_reqs.txt')
            run('bin/manage.py collectstatic --noinput')
            run('bin/manage.py syncdb')
            run('bin/manage.py migrate')
            sudo('service nginx reload')
            sudo('supervisorctl restart {}'.format(domain))


def web_run_command(domain, command):
    """ Run a command from the webroot directory of a domain on a production server """

    webroot = '/srv/www/{}/pri/venv/webroot'.format(domain)
    with cd(webroot):
        with prefix('source {}/../bin/activate'.format(webroot)):
            run(command)







