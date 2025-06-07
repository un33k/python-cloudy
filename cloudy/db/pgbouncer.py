import os
from fabric import task
from cloudy.util.context import Context
from cloudy.sys.etc import sys_etc_git_commit


@task
@Context.wrap_context
def db_pgbouncer_install(c: Context) -> None:
    """Install pgbouncer."""
    c.sudo('apt -y install pgbouncer')
    sys_etc_git_commit(c, 'Installed pgbouncer')


@task
@Context.wrap_context
def db_pgbouncer_configure(
    c: Context, dbhost: str = '', dbport: int = 5432
) -> None:
    """Configure pgbouncer with given dbhost and dbport."""
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'pgbouncer/pgbouncer.ini'))
    remotecfg = '/etc/pgbouncer/pgbouncer.ini'
    c.sudo(f'rm -rf {remotecfg}')
    c.put(localcfg, remotecfg)
    c.sudo(f'sed -i "s/dbport/{dbport}/g" {remotecfg}')
    if dbhost:
        c.sudo(f'sed -i "s/dbhost/{dbhost}/g" {remotecfg}')

    localdefault = os.path.expanduser(os.path.join(cfgdir, 'pgbouncer/default-pgbouncer'))
    remotedefault = '/etc/default/pgbouncer'
    c.sudo(f'rm -rf {remotedefault}')
    c.put(localdefault, remotedefault)
    sys_etc_git_commit(c, 'Configured pgbouncer')


@task
@Context.wrap_context
def db_pgbouncer_set_user_password(
    c: Context, user: str, password: str
) -> None:
    """Add user:pass to auth_user in pgbouncer userlist.txt."""
    userlist = '/etc/pgbouncer/userlist.txt'
    c.sudo(f'touch {userlist}')
    c.sudo(f'echo \'"{user}" "{password}"\' >> {userlist}')
    c.sudo(f'chown postgres:postgres {userlist}')
    c.sudo(f'chmod 600 {userlist}')







