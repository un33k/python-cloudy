import os

from fabric import task

from cloudy.sys.core import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def db_pgpool2_install(c: Context) -> None:
    """Install pgpool2."""
    c.sudo("apt -y install pgpool2")
    sys_etc_git_commit(c, "Installed pgpool2")


@task
@Context.wrap_context
def db_pgpool2_configure(
    c: Context, dbhost: str = "", dbport: str = "5432", localport: str = "5432"
) -> None:
    """Configure pgpool2 with given dbhost, dbport, and localport."""
    cfgdir = os.path.join(os.path.dirname(__file__), "../cfg")
    localcfg = os.path.expanduser(os.path.join(cfgdir, "pgpool2/pgpool.conf"))
    remotecfg = "/etc/pgpool2/pgpool.conf"
    c.sudo(f"rm -rf {remotecfg}")
    c.put(localcfg, "/tmp/pgpool.conf")
    c.sudo(f"mv /tmp/pgpool.conf {remotecfg}")
    c.sudo(f'sed -i "s/dbhost/{dbhost}/g" {remotecfg}')
    c.sudo(f'sed -i "s/dbport/{dbport}/g" {remotecfg}')
    c.sudo(f'sed -i "s/localport/{localport}/g" {remotecfg}')

    localdefault = os.path.expanduser(os.path.join(cfgdir, "pgpool2/default-pgpool2"))
    remotedefault = "/etc/default/pgpool2"
    c.sudo(f"rm -rf {remotedefault}")
    c.put(localdefault, "/tmp/default-pgpool2")
    c.sudo(f"mv /tmp/default-pgpool2 {remotedefault}")
    sys_etc_git_commit(c, "Configured pgpool2")
    sys_restart_service(c, "pgpool2")
