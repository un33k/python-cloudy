import os
import re
import sys
import datetime
from fabric.api import run, sudo, put, settings, hide
from fabric.contrib import files
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_start_service


def db_psql_install_postgres_repo():
    """Install the official postgres repository."""
    sudo('echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list')
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    sudo('apt update')

def db_psql_latest_version():
    """Get the latest available postgres version."""
    db_psql_install_postgres_repo()
    latest_version = ''
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        ret = run('apt-cache search --names-only postgresql-client')
    version_re = re.compile(r'postgresql-client-([0-9.]*)\s-')
    versions = [ver.group(1) for line in ret.split('\n') if (ver := version_re.search(line.lower()))]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass
    print(f'Latest available postgresql is: [{latest_version}]', file=sys.stderr)
    return latest_version

def db_psql_default_installed_version():
    """Get the default installed postgres version."""
    default_version = ''
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        ret = run('psql --version | head -1')
    version_re = re.compile(r'(.*)\s([0-9.]*)')
    ver = version_re.search(ret.lower())
    if ver:
        default_version = ver.group(2)[:3]
    print(f'Default installed postgresql is: [{default_version}]', file=sys.stderr)
    return default_version

def db_psql_install(version=''):
    """Install postgres of a given version or the latest version."""
    db_psql_install_postgres_repo()
    if not version:
        version = db_psql_latest_version()
    requirements = ' '.join([
        f'postgresql-{version}',
        f'postgresql-client-{version}',
        f'postgresql-contrib-{version}',
        f'postgresql-server-dev-{version}',
        'postgresql-client-common'
    ])
    sudo(f'apt -y install {requirements}')
    sys_etc_git_commit(f'Installed postgres ({version})')

def db_psql_client_install(version=''):
    """Install postgres client of a given version or the latest version."""
    if not version:
        version = db_psql_latest_version()
    requirements = ' '.join([
        f'postgresql-client-{version}',
        f'postgresql-server-dev-{version}',
    ])
    sudo(f'apt -y install {requirements}')
    sys_etc_git_commit(f'Installed postgres client ({version})')

def db_psql_make_data_dir(version='', data_dir='/var/lib/postgresql'):
    """Make data directory for the postgres cluster."""
    if not version:
        version = db_psql_latest_version()
    data_dir = os.path.abspath(os.path.join(data_dir, f'{version}'))
    sudo(f'mkdir -p {data_dir}')
    return data_dir

def db_psql_remove_cluster(version, cluster):
    """Remove a cluster if exists."""
    with settings(warn_only=True):
        sudo(f'pg_dropcluster --stop {version} {cluster}')
    sys_etc_git_commit(f'Removed postgres cluster ({version} {cluster})')

def db_psql_create_cluster(version='', cluster='main', encoding='UTF-8', data_dir='/var/lib/postgresql'):
    """Make a new postgresql cluster."""
    if not version:
        version = db_psql_default_installed_version() or db_psql_latest_version()
    db_psql_remove_cluster(version, cluster)
    data_dir = db_psql_make_data_dir(version, data_dir)
    sudo(f'chown -R postgres {data_dir}')
    sudo(f'pg_createcluster --start -e {encoding} {version} {cluster} -d {data_dir}')
    sys_start_service('postgresql')
    sys_etc_git_commit(f'Created new postgres cluster ({version} {cluster})')

def db_psql_set_permission(version='', cluster='main'):
    """Set default permission for postgresql."""
    if not version:
        version = db_psql_default_installed_version()
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'postgresql/pg_hba.conf'))
    remotecfg = f'/etc/postgresql/{version}/{cluster}/pg_hba.conf'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    sudo(f'chown postgres:postgres {remotecfg}')
    sudo(f'chmod 644 {remotecfg}')
    sys_start_service('postgresql')
    sys_etc_git_commit(f'Set default postgres access for cluster ({version} {cluster})')

def db_psql_configure(version='', cluster='main', port='5432', interface='*', restart=False):
    """Configure postgres."""
    if not version:
        version = db_psql_default_installed_version()
    conf_dir = f'/etc/postgresql/{version}/{cluster}'
    postgresql_conf = os.path.abspath(os.path.join(conf_dir, 'postgresql.conf'))
    sudo(f'sed -i "s/#listen_addresses\s\+=\s\+\'localhost\'/listen_addresses = \'{interface},127.0.0.1\'/g" {postgresql_conf}')
    sys_etc_git_commit(f'Configured postgres cluster ({version} {cluster})')
    if restart:
        sys_start_service('postgresql')

def db_psql_create_adminpack():
    """Install admin pack."""
    sudo('echo "CREATE EXTENSION adminpack;" | sudo -u postgres psql')

def db_psql_user_password(username, password):
    """Change password for a postgres user."""
    sudo(f'echo "ALTER USER {username} WITH ENCRYPTED PASSWORD \'{password}\';" | sudo -u postgres psql')

def db_psql_create_user(username, password):
    """Create postgresql user."""
    sudo(f'echo "CREATE ROLE {username} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN ENCRYPTED PASSWORD \'{password}\';" | sudo -u postgres psql')

def db_psql_delete_user(username):
    """Delete postgresql user."""
    if username != 'postgres':
        sudo(f'echo "DROP ROLE {username};" | sudo -u postgres psql')
    else:
        print("Cannot drop user 'postgres'", file=sys.stderr)

def db_psql_list_users():
    """List postgresql users."""
    sudo('sudo -u postgres psql -d template1 -c "SELECT * from pg_user;"')

def db_psql_list_databases():
    """List postgresql databases."""
    sudo('sudo -u postgres psql -l')

def db_psql_create_database(dbname, dbowner):
    """Create a postgres database for an existing user."""
    sudo(f'sudo -u postgres createdb -E UTF8 {dbname}')
    db_psql_grant_database_privileges(dbname, dbowner)

def db_psql_add_gis_extension_to_database(dbname):
    """Add gis extension to an existing database."""
    with settings(warn_only=True):
        sudo(f'sudo -u postgres psql -d {dbname} -c "CREATE EXTENSION postgis;"')

def db_psql_add_gis_topology_extension_to_database(dbname):
    """Add gis topology extension to an existing database."""
    with settings(warn_only=True):
        sudo(f'sudo -u postgres psql -d {dbname} -c "CREATE EXTENSION postgis_topology;"')

def db_psql_create_gis_database_from_template(dbname, dbowner):
    """Create a postgres GIS database from template for an existing user."""
    sudo(f'sudo -u postgres createdb -T template_postgis {dbname}')
    db_psql_grant_database_privileges(dbname, dbowner)

def db_psql_create_gis_database(dbname, dbowner):
    """Create a postgres GIS database for an existing user."""
    db_psql_create_database(dbname, dbowner)
    db_psql_add_gis_extension_to_database(dbname)
    db_psql_add_gis_topology_extension_to_database(dbname)

def db_psql_delete_database(dbname):
    """Delete (drop) a database."""
    sudo(f'echo "DROP DATABASE {dbname};" | sudo -u postgres psql')

def db_psql_grant_database_privileges(dbname, dbuser):
    """Grant all privileges on database for an existing user."""
    sudo(f'echo "GRANT ALL PRIVILEGES ON DATABASE {dbname} to {dbuser};" | sudo -u postgres psql')

def db_psql_dump_database(dump_dir, db_name, dump_name=''):
    """Backup (dump) a database and save into a given directory."""
    if not files.exists(dump_dir):
        sudo(f'mkdir -p {dump_dir}')
    if not dump_name:
        now = datetime.datetime.now()
        dump_name = f"{db_name}_{now.year}_{now.month}_{now.day}_{now.hour}_{now.second}.psql.gz"
    dump_name = os.path.join(dump_dir, dump_name)
    pg_dump = '/usr/bin/pg_dump'
    if not files.exists(pg_dump):
        pg_dump = run('which pg_dump')
    if files.exists(pg_dump):
        sudo(f'sudo -u postgres {pg_dump} --no-owner --no-acl -h localhost {db_name} | gzip > {dump_name}')



