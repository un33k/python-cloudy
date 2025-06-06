import os
from fabric.api import sudo, put
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_restart_service


def db_pgpool2_install():
    """Install pgpool2."""
    sudo('apt -y install pgpool2')
    sys_etc_git_commit('Installed pgpool2')


def db_pgpool2_configure(dbhost='', dbport=5432, localport=5432):
    """Configure pgpool2 with given dbhost, dbport, and localport."""
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'pgpool2/pgpool.conf'))
    remotecfg = '/etc/pgpool2/pgpool.conf'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    sudo(f'sed -i "s/dbhost/{dbhost}/g" {remotecfg}')
    sudo(f'sed -i "s/dbport/{dbport}/g" {remotecfg}')
    sudo(f'sed -i "s/localport/{localport}/g" {remotecfg}')

    localdefault = os.path.expanduser(os.path.join(cfgdir, 'pgpool2/default-pgpool2'))
    remotedefault = '/etc/default/pgpool2'
    sudo(f'rm -rf {remotedefault}')
    put(localdefault, remotedefault, use_sudo=True)
    sys_etc_git_commit('Configured pgpool2')
    sys_restart_service('pgpool2')





