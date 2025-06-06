import os
import re
import sys
import datetime
from typing import Optional
from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_start_service


@task
def db_psql_install_postgres_repo(c: Connection) -> None:
    """Install the official postgres repository."""
    c.sudo('echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list')
    c.sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    c.sudo('apt update')

@task
def db_psql_latest_version(c: Connection) -> str:
    """Get the latest available postgres version."""
    db_psql_install_postgres_repo(c)
    latest_version: str = ''
    result = c.run('apt-cache search --names-only postgresql-client', hide=True, warn=True)
    version_re = re.compile(r'postgresql-client-([0-9.]*)\s-')
    versions = [ver.group(1) for line in result.stdout.split('\n') if (ver := version_re.search(line.lower()))]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass
    print(f'Latest available postgresql is: [{latest_version}]', file=sys.stderr)
    return latest_version

def db_psql_default_installed_version(c: Connection) -> str:
    """Get the default installed postgres version."""
    default_version: str = ''
    result = c.run('psql --version | head -1', hide=True, warn=True)
    version_re = re.compile(r'(.*)\s([0-9.]*)')
    ver = version_re.search(result.stdout.lower())
    if ver:
        default_version = ver.group(2)[:3]
    print(f'Default installed postgresql is: [{default_version}]', file=sys.stderr)
    return default_version

@task
def db_psql_install(c: Connection, version: str = '') -> None:
    """Install postgres of a given version or the latest version."""
    db_psql_install_postgres_repo(c)
    if not version:
        version = db_psql_latest_version(c)
    requirements = ' '.join([
        f'postgresql-{version}',
        f'postgresql-client-{version}',
        f'postgresql-contrib-{version}',
        f'postgresql-server-dev-{version}',
        'postgresql-client-common'
    ])
    c.sudo(f'apt -y install {requirements}')
    sys_etc_git_commit(c, f'Installed postgres ({version})')

@task
def db_psql_client_install(c: Connection, version: str = '') -> None:
    """Install postgres client of a given version or the latest version."""
    if not version:
        version = db_psql_latest_version(c)
    requirements = ' '.join([
        f'postgresql-client-{version}',
        f'postgresql-server-dev-{version}',
    ])
    c.sudo(f'apt -y install {requirements}')
    sys_etc_git_commit(c, f'Installed postgres client ({version})')

def db_psql_make_data_dir(c: Connection, version: str = '', data_dir: str = '/var/lib/postgresql') -> str:
    """Make data directory for the postgres cluster."""
    if not version:
        version = db_psql_latest_version(c)
    data_dir = os.path.abspath(os.path.join(data_dir, f'{version}'))
    c.sudo(f'mkdir -p {data_dir}')
    return data_dir

def db_psql_remove_cluster(c: Connection, version: str, cluster: str) -> None:
    """Remove a cluster if exists."""
    c.run(f'pg_dropcluster --stop {version} {cluster}', warn=True)
    sys_etc_git_commit(c, f'Removed postgres cluster ({version} {cluster})')

@task
def db_psql_create_cluster(
    c: Connection,
    version: str = '',
    cluster: str = 'main',
    encoding: str = 'UTF-8',
    data_dir: str = '/var/lib/postgresql'
) -> None:
    """Make a new postgresql cluster."""
    if not version:
        version = db_psql_default_installed_version(c) or db_psql_latest_version(c)
    db_psql_remove_cluster(c, version, cluster)
    data_dir = db_psql_make_data_dir(c, version, data_dir)
    c.sudo(f'chown -R postgres {data_dir}')
    c.sudo(f'pg_createcluster --start -e {encoding} {version} {cluster} -d {data_dir}')
    sys_start_service(c, 'postgresql')
    sys_etc_git_commit(c, f'Created new postgres cluster ({version} {cluster})')

@task
def db_psql_set_permission(
    c: Connection, version: str = '', cluster: str = 'main'
) -> None:
    """Set default permission for postgresql."""
    if not version:
        version = db_psql_default_installed_version(c)
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'postgresql/pg_hba.conf'))
    remotecfg = f'/etc/postgresql/{version}/{cluster}/pg_hba.conf'
    c.sudo(f'rm -rf {remotecfg}')
    c.put(localcfg, remotecfg)
    c.sudo(f'chown postgres:postgres {remotecfg}')
    c.sudo(f'chmod 644 {remotecfg}')
    sys_start_service(c, 'postgresql')
    sys_etc_git_commit(c, f'Set default postgres access for cluster ({version} {cluster})')

@task
def db_psql_configure(
    c: Connection,
    version: str = '',
    cluster: str = 'main',
    port: str = '5432',
    interface: str = '*',
    restart: bool = False
) -> None:
    """Configure postgres."""
    if not version:
        version = db_psql_default_installed_version(c)
    conf_dir = f'/etc/postgresql/{version}/{cluster}'
    postgresql_conf = os.path.abspath(os.path.join(conf_dir, 'postgresql.conf'))
    c.sudo(fr"sed -i \"s/#listen_addresses\s\+=\s\+'localhost'/listen_addresses = '{interface},127.0.0.1'/g\" {postgresql_conf}")
    sys_etc_git_commit(c, f'Configured postgres cluster ({version} {cluster})')
    if restart:
        sys_start_service(c, 'postgresql')

@task
def db_psql_create_adminpack(c: Connection) -> None:
    """Install admin pack."""
    c.sudo('echo "CREATE EXTENSION adminpack;" | sudo -u postgres psql')

@task
def db_psql_user_password(c: Connection, username: str, password: str) -> None:
    """Change password for a postgres user."""
    c.sudo(f'echo "ALTER USER {username} WITH ENCRYPTED PASSWORD \'{password}\';" | sudo -u postgres psql')

@task
def db_psql_create_user(c: Connection, username: str, password: str) -> None:
    """Create postgresql user."""
    c.sudo(f'echo "CREATE ROLE {username} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN ENCRYPTED PASSWORD \'{password}\';" | sudo -u postgres psql')

@task
def db_psql_delete_user(c: Connection, username: str) -> None:
    """Delete postgresql user."""
    if username != 'postgres':
        c.sudo(f'echo "DROP ROLE {username};" | sudo -u postgres psql')
    else:
        print("Cannot drop user 'postgres'", file=sys.stderr)

@task
def db_psql_list_users(c: Connection) -> None:
    """List postgresql users."""
    c.sudo('sudo -u postgres psql -d template1 -c "SELECT * from pg_user;"')

@task
def db_psql_list_databases(c: Connection) -> None:
    """List postgresql databases."""
    c.sudo('sudo -u postgres psql -l')

@task
def db_psql_create_database(c: Connection, dbname: str, dbowner: str) -> None:
    """Create a postgres database for an existing user."""
    c.sudo(f'sudo -u postgres createdb -E UTF8 {dbname}')
    db_psql_grant_database_privileges(c, dbname, dbowner)

@task
def db_psql_add_gis_extension_to_database(c: Connection, dbname: str) -> None:
    """Add gis extension to an existing database."""
    c.sudo(f'sudo -u postgres psql -d {dbname} -c "CREATE EXTENSION postgis;"', warn=True)

@task
def db_psql_add_gis_topology_extension_to_database(c: Connection, dbname: str) -> None:
    """Add gis topology extension to an existing database."""
    c.sudo(f'sudo -u postgres psql -d {dbname} -c "CREATE EXTENSION postgis_topology;"', warn=True)

@task
def db_psql_create_gis_database_from_template(c: Connection, dbname: str, dbowner: str) -> None:
    """Create a postgres GIS database from template for an existing user."""
    c.sudo(f'sudo -u postgres createdb -T template_postgis {dbname}')
    db_psql_grant_database_privileges(c, dbname, dbowner)

@task
def db_psql_create_gis_database(c: Connection, dbname: str, dbowner: str) -> None:
    """Create a postgres GIS database for an existing user."""
    db_psql_create_database(c, dbname, dbowner)
    db_psql_add_gis_extension_to_database(c, dbname)
    db_psql_add_gis_topology_extension_to_database(c, dbname)

@task
def db_psql_delete_database(c: Connection, dbname: str) -> None:
    """Delete (drop) a database."""
    c.sudo(f'echo "DROP DATABASE {dbname};" | sudo -u postgres psql')

@task
def db_psql_grant_database_privileges(c: Connection, dbname: str, dbuser: str) -> None:
    """Grant all privileges on database for an existing user."""
    c.sudo(f'echo "GRANT ALL PRIVILEGES ON DATABASE {dbname} to {dbuser};" | sudo -u postgres psql')

@task
def db_psql_dump_database(c: Connection, dump_dir: str, db_name: str, dump_name: Optional[str] = None) -> None:
    """Backup (dump) a database and save into a given directory."""
    # Check if directory exists, create if not
    result = c.run(f'test -d {dump_dir}', warn=True)
    if result.failed:
        c.sudo(f'mkdir -p {dump_dir}')
    if not dump_name:
        now = datetime.datetime.now()
        dump_name = f"{db_name}_{now.year}_{now.month}_{now.day}_{now.hour}_{now.second}.psql.gz"
    dump_name = os.path.join(dump_dir, dump_name)
    pg_dump = '/usr/bin/pg_dump'
    result = c.run(f'test -x {pg_dump}', warn=True)
    if result.failed:
        pg_dump = c.run('which pg_dump', hide=True).stdout.strip()
    if pg_dump:
        c.sudo(f'sudo -u postgres {pg_dump} --no-owner --no-acl -h localhost {db_name} | gzip > {dump_name}')



