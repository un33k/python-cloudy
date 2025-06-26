import os

from fabric import task

from cloudy.sys.core import sys_add_default_startup, sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port
from cloudy.util.context import Context


@task
@Context.wrap_context
def web_supervisor_install(c: Context):
    """Install Supervisor and bootstrap configuration."""
    c.sudo("apt -y install supervisor")
    web_supervisor_bootstrap(c)
    sys_etc_git_commit(c, "Installed Supervisor")


@task
@Context.wrap_context
def web_supervisor_bootstrap(c: Context):
    """Bootstrap Supervisor configuration from local templates."""
    c.sudo("rm -rf /etc/supervisor/*")
    cfgdir = os.path.join(os.path.dirname(__file__), "../cfg")
    localcfg = os.path.expanduser(os.path.join(cfgdir, "supervisor/supervisord.conf"))
    remotecfg = "/etc/supervisor/supervisord.conf"

    c.put(localcfg, remotecfg, use_sudo=True)
    c.sudo("mkdir -p /etc/supervisor/sites-available")
    c.sudo("mkdir -p /etc/supervisor/sites-enabled")
    c.sudo("chown -R root:root /etc/supervisor")
    c.sudo("chmod -R 644 /etc/supervisor")
    sys_add_default_startup(c, "supervisor")
    sys_restart_service(c, "supervisor")


@task
@Context.wrap_context
def web_supervisor_setup_domain(c: Context, domain, port=None, interface="0.0.0.0", worker_num=3):
    """Setup Supervisor config file for a domain."""
    supervisor_avail_dir = "/etc/supervisor/sites-available"
    supervisor_enabled_dir = "/etc/supervisor/sites-enabled"

    cfgdir = os.path.join(os.path.dirname(__file__), "../cfg")
    localcfg = os.path.expanduser(os.path.join(cfgdir, "supervisor/site.conf"))
    remotecfg = f"{supervisor_avail_dir}/{domain}.conf"
    c.sudo(f"rm -rf {remotecfg}")
    c.put(localcfg, remotecfg, use_sudo=True)
    if not port:
        port = sys_show_next_available_port(c)
    c.sudo(f'sed -i "s/bound_address/{interface}/g" {remotecfg}')
    c.sudo(f'sed -i "s/port_num/{port}/g" {remotecfg}')
    c.sudo(f'sed -i "s/worker_num/{worker_num}/g" {remotecfg}')
    escaped_domain = domain.replace(".", "\\.")
    c.sudo(f'sed -i "s/example\\.com/{escaped_domain}/g" {remotecfg}')
    c.sudo(f"chown -R root:root {supervisor_avail_dir}")
    c.sudo(f"chmod -R 755 {supervisor_avail_dir}")
    with c.cd(supervisor_enabled_dir):
        c.sudo(f"ln -sf {remotecfg}")
    sys_restart_service(c, "supervisor")
    c.sudo(f"supervisorctl restart {domain}")
    sys_etc_git_commit(c, f"Setup Supervisor Config for Domain {domain}")
