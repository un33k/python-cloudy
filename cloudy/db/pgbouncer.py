import os
from fabric.api import sudo, put
from cloudy.sys.etc import sys_etc_git_commit


def db_pgbouncer_install():
    """Install pgbouncer."""
    sudo('apt -y install pgbouncer')
    sys_etc_git_commit('Installed pgbouncer')


def db_pgbouncer_configure(dbhost='', dbport=5432):
    """Configure pgbouncer with given dbhost and dbport."""
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'pgbouncer/pgbouncer.ini'))
    remotecfg = '/etc/pgbouncer/pgbouncer.ini'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    sudo(f'sed -i "s/dbport/{dbport}/g" {remotecfg}')
    if dbhost:
        sudo(f'sed -i "s/dbhost/{dbhost}/g" {remotecfg}')

    localdefault = os.path.expanduser(os.path.join(cfgdir, 'pgbouncer/default-pgbouncer'))
    remotedefault = '/etc/default/pgbouncer'
    sudo(f'rm -rf {remotedefault}')
    put(localdefault, remotedefault, use_sudo=True)

    sys_etc_git_commit('Configured pgbouncer')


def db_pgbouncer_set_user_password(user, password):
    """Add user:pass to auth_user in pgbouncer userlist.txt."""
    userlist = '/etc/pgbouncer/userlist.txt'
    sudo(f'touch {userlist}')
    sudo(f'echo \'"{user}" "{password}"\' >> {userlist}')
    sudo(f'chown postgres:postgres {userlist}')
    sudo(f'chmod 600 {userlist}')







