import re
import sys
from operator import itemgetter
from fabric.api import run, sudo, settings, hide
from fabric.contrib import files
from cloudy.sys.etc import sys_etc_git_commit


def db_mysql_latest_version():
    """Get the latest available MySQL version."""

    latest_version = ''
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        ret = run('apt-cache search --names-only mysql-client')

    version_re = re.compile(r'mysql-client-([0-9.]+)\s-')
    versions = [ver.group(1) for line in ret.split('\n') if (ver := version_re.search(line.lower()))]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass

    print(f'Latest available mysql is: [{latest_version}]', file=sys.stderr)
    return latest_version


def db_mysql_server_install(version=''):
    """Install MySQL Server."""

    if not version:
        version = db_mysql_latest_version()

    requirements = f'mysql-server-{version}'
    sudo(f'DEBIAN_FRONTEND=noninteractive apt -y install {requirements}')
    sys_etc_git_commit(f'Installed MySQL Server ({version})')


def db_mysql_client_install(version=''):
    """Install MySQL Client."""

    if not version:
        version = db_mysql_latest_version()

    requirements = f'mysql-client-{version}'
    sudo(f'DEBIAN_FRONTEND=noninteractive apt -y install {requirements}')
    sys_etc_git_commit(f'Installed MySQL Client ({version})')


def db_mysql_set_root_password(password):
    """Set MySQL root password."""

    if not password:
        print('Password required for mysql root', file=sys.stderr)
        return

    sudo(f'mysqladmin -u root password {password}')
    sys_etc_git_commit('Set MySQL Root Password')


def db_mysql_create_database(root_pass, db_name):
    """Create a new MySQL database."""

    sudo(f'echo "CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" | sudo mysql -u root -p{root_pass}')


def db_mysql_create_user(root_pass, user, user_pass):
    """Create a new MySQL user."""

    sudo(f'echo "CREATE USER \'{user}\'@\'localhost\' IDENTIFIED BY \'{user_pass}\';" | sudo mysql -u root -p{root_pass}')


def db_mysql_grant_user(root_pass, user, database):
    """Grant all privileges on a database to a user."""

    sudo(f'echo "GRANT ALL PRIVILEGES ON {database}.* TO \'{user}\'@\'localhost\';" | sudo mysql -u root -p{root_pass}')
    sudo(f'echo "FLUSH PRIVILEGES;" | sudo mysql -u root -p{root_pass}')


