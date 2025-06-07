import re
import sys
from operator import itemgetter
from fabric import task
from cloudy.util.context import Context
from cloudy.sys.etc import sys_etc_git_commit


@task
@Context.wrap_context
def db_mysql_latest_version(c: Context) -> str:
    """Get the latest available MySQL version."""
    latest_version: str = ''
    result = c.run('apt-cache search --names-only mysql-client', hide=True, warn=True)
    version_re = re.compile(r'mysql-client-([0-9.]+)\s-')
    versions = [ver.group(1) for line in result.stdout.split('\n') if (ver := version_re.search(line.lower()))]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass

    print(f'Latest available mysql is: [{latest_version}]', file=sys.stderr)
    return latest_version


@task
@Context.wrap_context
def db_mysql_server_install(c: Context, version: str = '') -> None:
    """Install MySQL Server."""
    if not version:
        version = db_mysql_latest_version(c)
    requirements = f'mysql-server-{version}'
    c.sudo(f'DEBIAN_FRONTEND=noninteractive apt -y install {requirements}')
    sys_etc_git_commit(c, f'Installed MySQL Server ({version})')


@task
@Context.wrap_context
def db_mysql_client_install(c: Context, version: str = '') -> None:
    """Install MySQL Client."""
    if not version:
        version = db_mysql_latest_version(c)
    requirements = f'mysql-client-{version}'
    c.sudo(f'DEBIAN_FRONTEND=noninteractive apt -y install {requirements}')
    sys_etc_git_commit(c, f'Installed MySQL Client ({version})')


@task
@Context.wrap_context
def db_mysql_set_root_password(c: Context, password: str) -> None:
    """Set MySQL root password."""
    if not password:
        print('Password required for mysql root', file=sys.stderr)
        return
    c.sudo(f'mysqladmin -u root password {password}')
    sys_etc_git_commit(c, 'Set MySQL Root Password')


@task
@Context.wrap_context
def db_mysql_create_database(c: Context, root_pass: str, db_name: str) -> None:
    """Create a new MySQL database."""
    c.sudo(f'echo "CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" | sudo mysql -u root -p{root_pass}')


@task
@Context.wrap_context
def db_mysql_create_user(c: Context, root_pass: str, user: str, user_pass: str) -> None:
    """Create a new MySQL user."""
    c.sudo(f'echo "CREATE USER \'{user}\'@\'localhost\' IDENTIFIED BY \'{user_pass}\';" | sudo mysql -u root -p{root_pass}')


@task
@Context.wrap_context
def db_mysql_grant_user(c: Context, root_pass: str, user: str, database: str) -> None:
    """Grant all privileges on a database to a user."""
    c.sudo(f'echo "GRANT ALL PRIVILEGES ON {database}.* TO \'{user}\'@\'localhost\';" | sudo mysql -u root -p{root_pass}')
    c.sudo(f'echo "FLUSH PRIVILEGES;" | sudo mysql -u root -p{root_pass}')


