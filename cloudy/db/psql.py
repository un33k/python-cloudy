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
from cloudy.util.common import sys_start_service


def db_psql_install_postgres_repo():
    """
    Installs the official postgres repository.
    """
    sudo('echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list')
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    sudo('apt update')

def db_psql_latest_version():
    """ Get the latest available postgres version - Ex: (cmd)"""

    db_psql_install_postgres_repo()

    latest_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('apt-cache search --names-only postgresql-client')

    version_re = re.compile('postgresql-client-([0-9.]*)\s-')
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

    print >> sys.stderr, 'Latest available postgresql is: [{}]'.format(latest_version)
    return latest_version


def db_psql_default_installed_version():
    """ Get the default installed postgres version - Ex: (cmd) """

    default_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('psql --version | head -1')

    version_re = re.compile('(.*)\s([0-9.]*)')
    ver = version_re.search(ret.lower())
    if ver:
        default_version = ver.group(2)[:3]

    print >> sys.stderr, 'Default installed postgresql is: [{}]'.format(default_version)
    return default_version

def db_psql_install(version=''):
    """ Install postgres of a given version or the latest version - Ex: (cmd:[9.1])"""

    db_psql_install_postgres_repo()

    if not version:
        version = db_psql_latest_version()

    # requirements
    requirements = '%s' % ' '.join([
        'postgresql-{}'.format(version),
        'postgresql-client-{}'.format(version),
        'postgresql-contrib-{}'.format(version),
        'postgresql-server-dev-{}'.format(version),
        'postgresql-client-common'
    ])

    # install requirements
    sudo('apt -y install {}'.format(requirements))
    sys_etc_git_commit('Installed postgres ({})'.format(version))

def db_psql_client_install(version=''):
    """ Install postgres of a given version or the latest version - Ex: (cmd:[9.1])"""

    if not version:
        version = db_psql_latest_version()

    # requirements
    requirements = '%s' % ' '.join([
        'postgresql-client-{}'.format(version),
        'postgresql-server-dev-{}'.format(version),
    ])

    # install requirements
    sudo('apt -y install {}'.format(requirements))
    sys_etc_git_commit('Installed postgres ({})'.format(version))


def db_psql_make_data_dir(version='', data_dir='/var/lib/postgresql'):
    """ Make data directory for the postgres cluster - Ex: (cmd:[pgversion],[datadir])"""

    if not version:
        version =db_psql_latest_version()

    data_dir = os.path.abspath(os.path.join(data_dir, '{}'.format(version)))
    sudo('mkdir -p {}'.format(data_dir))
    return data_dir


def db_psql_remove_cluster(version, cluster):
    """ Remove a clauster if exists - Ex: (cmd:<pgversion><cluster>)"""

    with settings(warn_only=True):
        sudo('pg_dropcluster --stop {} {}'.format(version, cluster))

    sys_etc_git_commit('Removed postgres cluster ({} {})'.format(version, cluster))


def db_psql_create_cluster(version='', cluster='main', encoding='UTF-8', data_dir='/var/lib/postgresql'):
    """ Make a new postgresql clauster - Ex: (cmd:[pgversion],[cluster],[encoding],[datadir])"""

    if not version:
        version = db_psql_default_installed_version()
    if not version:
        version = db_psql_latest_version()

    db_psql_remove_cluster(version, cluster)

    data_dir = db_psql_make_data_dir(version, data_dir)
    sudo('chown -R postgres {}'.format(data_dir))
    sudo('pg_createcluster --start -e {} {} {} -d {}'.format(encoding, version, cluster, data_dir))
    sys_start_service('postgresql');
    sys_etc_git_commit('Created new postgres cluster ({} {})'.format(version, cluster))

def db_psql_set_permission(version='', cluster='main'):
    """ Set default permission for postgresql - Ex: (cmd:<version>,[cluster])"""
    if not version:
        version = db_psql_default_installed_version()

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'postgresql/pg_hba.conf'))
    remotecfg = '/etc/postgresql/{}/{}/pg_hba.conf'.format(version, cluster)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sudo('chown postgres:postgres {}'.format(remotecfg))
    sudo('chmod 644 {}'.format(remotecfg))
    sys_start_service('postgresql');
    sys_etc_git_commit('Set default postgres access for cluster ({} {})'.format(version, cluster))

def db_psql_configure(version='', cluster='main', port='5432', interface='*', restart=False):
    """ Configure postgres - Ex: (cmd:[pgversion],[cluster],[port],[interface])"""
    if not version:
        version = db_psql_default_installed_version()

    """ Configures posgresql configuration files """
    conf_dir = '/etc/postgresql/{}/{}'.format(version, cluster)
    postgresql_conf = os.path.abspath(os.path.join(conf_dir, 'postgresql.conf'))
    sudo('sed -i "s/#listen_addresses\s\+=\s\+\'localhost\'/listen_addresses = \'{}\'/g" {}'.format(interface+',127.0.0.1', postgresql_conf))

    # total_mem = sudo("free -m | head -2 | grep Mem | awk '{print $2}'")
    # shared_buffers = eval(total_mem) / 4
    # sudo('sed -i "s/shared_buffers\s\+=\s\+[0-9]\+MB/shared_buffers = {}MB/g" {}'.format(shared_buffers, postgresql_conf))

    sys_etc_git_commit('Configured postgres cluster ({} {})'.format(version, cluster))
    if restart:
        sys_start_service('postgresql')

def db_psql_create_adminpack():
    """ Install admin pack - Ex: (cmd)"""
    sudo('echo "CREATE EXTENSION adminpack;" | sudo -u postgres psql')


def db_psql_user_password(username, password):
    """ Change password for user: postgres - Ex: (cmd:<username>,<password>)"""
    sudo('echo "ALTER USER {} WITH ENCRYPTED PASSWORD \'{}\';" | sudo -u postgres psql'.format(username, password))


def db_psql_create_user(username, password):
    """ Create postgresql user - Ex: (cmd:<dbuser>,<dbname>)"""
    sudo('echo "CREATE ROLE {} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN ENCRYPTED PASSWORD \'{}\';" | sudo -u postgres psql'.format(username, password))


def db_psql_delete_user(username):
    """ Delete postgresql user - Ex: (cmd:<dbuser>)"""
    if username != 'postgres':
        sudo('echo "DROP ROLE {};" | sudo -u postgres psql'.format(username))
    else:
        print >> sys.stderr, "Cannot drop user 'postgres'"


def db_psql_list_users():
    """ List postgresql users - Ex: (cmd)"""
    sudo('sudo -u postgres psql -d template1 -c \"SELECT * from pg_user;\"')


def db_psql_list_databases():
    """ List postgresql databases - Ex: (cmd)"""
    sudo('sudo -u postgres psql -l')


def db_psql_create_database(dbname, dbowner):
    """ Create a postgres database for an existing user - Ex: (cmd:<dbname>,<dbowner>)"""
    sudo('sudo -u postgres createdb -E UTF8 {}'.format(dbname))
    db_psql_grant_database_privileges(dbname, dbowner)


def db_psql_add_gis_extension_to_database(dbname):
    """ Add gis extension to an existing database - Ex: (cmd:<dbname>)"""
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d {} -c \"CREATE EXTENSION postgis;\"'.format(dbname))


def db_psql_add_gis_topology_extension_to_database(dbname):
    """ Add gis topology extension to an existing database - Ex: (cmd:<dbname>)"""
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d {} -c \"CREATE EXTENSION postgis_topology;\"'.format(dbname))


def db_psql_create_gis_database_from_template(dbname, dbowner):
    """ Create a postgres GIS database base on existing template, for an existing user - Ex: (cmd:<dbname>,<dbowner>)"""
    sudo('sudo -u postgres createdb -T template_postgis {}'.format(dbname))
    db_psql_grant_database_privileges(dbname, dbowner)


def db_psql_create_gis_database(dbname, dbowner):
    """ Create a postgres GIS database for an existing user - Ex: (cmd:<dbname>,<dbowner>)"""
    db_psql_create_database(dbname, dbowner)
    db_psql_add_gis_extension_to_database(dbname)
    db_psql_add_gis_topology_extension_to_database(dbname)


def db_psql_delete_database(dbname):
    """ Delete (drop) a database - Ex: (cmd:<dbname>) """
    sudo('echo "DROP DATABASE {};" | sudo -u postgres psql'.format(dbname))


def db_psql_grant_database_privileges(dbname, dbuser):
    """ Grant all privileges on database for an existing user - Ex: (cmd:<dbname>,<dbuser>)"""
    sudo('echo "GRANT ALL PRIVILEGES ON DATABASE {} to {};" | sudo -u postgres psql'.format(dbname, dbuser))


def db_psql_dump_database(dump_dir, db_name, dump_name=''):
    """ Backup (dump) a database and save into a given directory - Ex: (cmd:<dumpdir>,<dbname>,[dumpname]) """
    if not files.exists(dump_dir):
        sudo('mkdir -p {}'.format(dump_dir))
    if not dump_name:
        now = datetime.datetime.now()
        dump_name = "{}_{}_{}_{}_{}_{}.psql.gz".format(db_name, now.year, now.month, now.day, now.hour, now.second)
    dump_name = os.path.join(dump_dir, dump_name)
    pg_dump = '/usr/bin/pg_dump'
    if not files.exists(pg_dump):
        pg_dump = run('which pg_dump')
    if files.exists(pg_dump):
        sudo('sudo -u postgres {} --no-owner --no-acl -h localhost {}| gzip > {}'.format(pg_dump, db_name, dump_name))



