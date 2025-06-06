import os
import re
import sys

from fabric.api import run, sudo, cd, prefix
from fabric.api import task
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_reload_service


def web_create_data_directory(web_dir='/srv/www'):
    """Create a data directory for the web files."""
    sudo(f'mkdir -p {web_dir}')


def web_create_shared_directory(shared_dir='/srv/www/shared'):
    """Create a shared directory for the site."""
    sudo(f'mkdir -p {shared_dir}')
    sudo(f'chown -R :www-data {shared_dir}')
    sudo(f'chmod -R g+wrx {shared_dir}')


def web_create_seekrets_directory(seekrets_dir='/srv/www/seekrets'):
    """Create a seekrets directory."""
    sudo(f'mkdir -p {seekrets_dir}')
    sudo(f'chown -R :www-data {seekrets_dir}')
    sudo(f'chmod -R g+wrx {seekrets_dir}')


def web_create_site_directory(domain):
    """Create a site directory structure for a domain."""
    path = f'/srv/www/{domain}'
    sudo(f'mkdir -p {path}/{{pri,pub,log,bck}}')
    sudo(f'chown -R :www-data {path}')
    sudo(f'chmod -R g+w {path}/pub')
    sudo(f'chmod -R g+w {path}/log')


def web_create_virtual_env(domain, py_version='3'):
    """Create a virtualenv for a domain."""
    path = f'/srv/www/{domain}/pri'
    with cd(path):
        sudo(f'python{py_version} -m venv venv')
        sudo('chown -R :www-data venv')
        sudo('chmod -R g+wrx venv')


def web_create_site_log_file(domain):
    """Create a log file with proper permissions for Django."""
    site_logfile = f'/srv/www/{domain}/log/{domain}.log'
    sudo(f'touch {site_logfile}')
    sudo(f'chown :www-data {site_logfile}')
    sudo(f'chmod g+rw {site_logfile}')


def web_prepare_site(domain, py_version='3'):
    """Create a site directory and everything else for the site on production server."""
    web_create_site_directory(domain)
    web_create_virtual_env(domain, py_version)
    web_create_site_log_file(domain)


def web_deploy(domain):
    """Push changes to a production server."""
    webroot = f'/srv/www/{domain}/pri/venv/webroot'
    with cd(webroot):
        with prefix(f'source {webroot}/../bin/activate'):
            run('git pull')
            run('pip install -r env/deploy_reqs.txt')
            run('bin/manage.py collectstatic --noinput')
            run('bin/manage.py migrate')
            sys_reload_service('nginx')
            sudo(f'supervisorctl restart {domain}')


def web_run_command(domain, command):
    """Run a command from the webroot directory of a domain on a production server."""
    webroot = f'/srv/www/{domain}/pri/venv/webroot'
    with cd(webroot):
        with prefix(f'source {webroot}/../bin/activate'):
            run(command)







