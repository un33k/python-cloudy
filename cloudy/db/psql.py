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
from fabric.contrib.files import sed

from cloudy.sys.etc import etc_git_commit


def psql_latest_version():
    """ Get the latest available postgres version """
    
    latest_version = ''
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
    
    print >> sys.stderr, 'Latest available postgresql is: [{0}]'.format(latest_version)
    return latest_version


def psql_default_installed_version():
    """ Get the default installed postgres version """

    default_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('psql --version | head -1')

    version_re = re.compile('(.*)\s([0-9.]*)')
    ver = version_re.search(ret.lower())
    if ver:
        default_version = ver.group(2)[:3]

    print >> sys.stderr, 'Default installed postgresql is: [{0}]'.format(default_version)
    return default_version
        
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
    sudo('apt-get -y install{0}'.format(requirements))
    etc_git_commit('Installed postgres ({0})'.format(version))


def psql_make_data_dir(version='', data_dir='/var/lib/postgresql'):
    """ Make data directory for the postgres cluster """
    
    if not version:
        version = psql_latest_version()

    data_dir = os.path.abspath(os.path.join(data_dir, '{0}'.format(version)))
    sudo('mkdir -p {0}'.format(data_dir))
    return data_dir


def psql_remove_cluster(version='', cluster='main'):
    """ Remove a clauster if exists """

    if not version:
        version = psql_default_installed_version()
    if not version:
        version = psql_latest_version()
        
    with settings(warn_only=True):
        sudo('pg_dropcluster --stop {0} {1}'.format(version, cluster))

    etc_git_commit('Removed postgres cluster ({0} {1})'.format(version, cluster))


def psql_create_cluster(version='', cluster='main', encoding='UTF-8', data_dir='/var/lib/postgresql'):
    """ Make a new clauster """

    if not version:
        version = psql_default_installed_version()
    if not version:
        version = psql_latest_version()

    psql_remove_cluster(version, cluster)
    
    data_dir = psql_make_data_dir(version, data_dir)
    sudo('chown -R postgres {0}'.format(data_dir))
    sudo('pg_createcluster --start -e {0} {1} {2} -d {3}'.format(encoding, version, cluster, data_dir))
    sudo('service postgresql start')
    etc_git_commit('Created new postgres cluster ({0} {1})'.format(version, cluster))


def psql_configure(version='', cluster='main', port='5432', listen='*'):
    if not version:
        version = psql_default_installed_version()

    """ Configures posgresql configuration files """
    conf_dir = '/etc/postgresql/{0}/{1}'.format(version, cluster)
    postgresql_conf = os.path.abspath(os.path.join(conf_dir, 'postgresql.conf'))
    sudo('sed -i "s/#listen_addresses\s\+=\s\+\'localhost\'/listen_addresses = \'*\'/g" {0}'.format(postgresql_conf))

    total_mem = sudo("free -m | head -2 | grep Mem | awk '{print $2}'")
    shared_buffers = eval(total_mem) / 4    
    sudo('sed -i "s/shared_buffers\s\+=\s\+[0-9]\+MB/shared_buffers = {0}MB/g" {1}'.format(shared_buffers, postgresql_conf))
    
    pg_hba_conf = os.path.abspath(os.path.join(conf_dir, 'pg_hba.conf'))
    sudo('echo \"host all all 0.0.0.0/0 md5\" >> {0}'.format(pg_hba_conf))
    
    etc_git_commit('Configured postgres cluster ({0} {1})'.format(version, cluster))
    
    sudo('service postgresql start')


def psql_postgres_password(password):
    sudo('echo "ALTER USER postgres WITH ENCRYPTED PASSWORD \'{0}\';" | sudo -u postgres psql'.format(password))





