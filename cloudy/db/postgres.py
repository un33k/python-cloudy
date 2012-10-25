import os
import re
import sys
from operator import itemgetter

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide

from cloudy.sys.etc import etc_git_commit

def psql_latest_version():
    """ Get the latest available postgres version """
    
    latest_version = '9.1'
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('apt-cache search postgresql-client')
    
    version_re = re.compile('postgresql-client-([0-9.]*)\s-')
    lines = ret.split('\n')
    versions = []
    for line in lines:
        ver = version_re.search(line.lower())
        if ver:
            versions.append(ver.group(1))
    
    versions.sort(key = itemgetter(2), reverse = False)
    try:
        latest_version = versions[0]
    except:
        pass
    return latest_version


def psql_default_installed_version():
    """ Get the default installed postgres version """

    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('psql --version | head -1')

    version_re = re.compile('(.*)\s([0-9.]*)')
    ver = version_re.search(ret.lower())
    if ver:
        return ver.group(2)[:3]

    return None
        
def psql_install(version=''):
    """ Install postgres of a given version or the latest version """
    if not version:
        version = psql_latest_version()
        
    # requirements
    requirements = '%s' % ' '.join([
        'postgresql-{0}'.format(version),
        'postgresql-client-{0}'.format(version),
        'postgresql-contrib-{0}'.format(version),
        'postgresql-server-dev-{0}'.format(version),
        'postgresql-client-common'
    ])
    
    # install requirements
    cmd = 'apt-get -y install'
    sudo('{0} {1}'.format(cmd, requirements))
    etc_git_commit('Installed postgres ({0})'.format(version))


def psql_make_data_dir(version='', data_dir='/var/lib/postgresql'):
    """ Make data directory for the postgres cluster """
    
    if not version:
        version = psql_latest_version()

    data_dir = os.path.abspath(os.path.join(data_dir, '{0}'.format(version), 'main'))
    cmd = 'mkdir -p '
    sudo('{0} {1}'.format(cmd, data_dir))
    return data_dir


def psql_remove_cluster(version=''):
    """ Remove a clauster if exists """

    if not version:
        version = psql_default_installed_version()
    if not version:
        version = psql_latest_version()
        
    cmd = 'pg_dropcluster --stop {0} main'.format(version)
    with settings(warn_only=True):
        sudo(cmd)

    etc_git_commit('Removed postgres cluster ({0} main)'.format(version))


def psql_create_cluster(version='', encoding='UTF-8', data_dir='/var/lib/postgresql'):
    """ Make a new clauster """

    if not version:
        version = psql_default_installed_version()
    if not version:
        version = psql_latest_version()

    psql_remove_cluster(version)
    
    data_dir = psql_make_data_dir(version, data_dir)
    cmd = 'chown -R postgres {0}'.format(data_dir)
    sudo(cmd)
    
    sudo('pg_createcluster --start -e {0} {1} main -d {2}'.format(encoding, version, data_dir))
    etc_git_commit('Removed postgres cluster ({0} main)'.format(version))







