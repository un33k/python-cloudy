import os
from fabric.api import sudo, put, cd
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port
from cloudy.util.common import sys_restart_service
from cloudy.sys.core import sys_add_default_startup


def web_supervisor_install():
    """Install Supervisor and bootstrap configuration."""
    sudo('apt -y install supervisor')
    web_supervisor_bootstrap()
    sys_etc_git_commit(c, 'Installed Supervisor')


def web_supervisor_bootstrap():
    """Bootstrap Supervisor configuration from local templates."""
    sudo('rm -rf /etc/supervisor/*')
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'supervisor/supervisord.conf'))
    remotecfg = '/etc/supervisor/supervisord.conf'

    put(localcfg, remotecfg, use_sudo=True)
    sudo('mkdir -p /etc/supervisor/sites-available')
    sudo('mkdir -p /etc/supervisor/sites-enabled')
    sudo('chown -R root:root /etc/supervisor')
    sudo('chmod -R 644 /etc/supervisor')
    sys_add_default_startup('supervisor')
    sys_restart_service(c, 'supervisor')


def web_supervisor_setup_domain(domain, port=None, interface='0.0.0.0', worker_num=3):
    """Setup Supervisor config file for a domain."""
    supervisor_avail_dir = '/etc/supervisor/sites-available'
    supervisor_enabled_dir = '/etc/supervisor/sites-enabled'

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'supervisor/site.conf'))
    remotecfg = f'{supervisor_avail_dir}/{domain}.conf'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    if not port:
        port = sys_show_next_available_port()
    sudo(f'sed -i "s/bound_address/{interface}/g" {remotecfg}')
    sudo(f'sed -i "s/port_num/{port}/g" {remotecfg}')
    sudo(f'sed -i "s/worker_num/{worker_num}/g" {remotecfg}')
    sudo(f'sed -i "s/example\\.com/{domain.replace(".", "\\.")}/g" {remotecfg}')
    sudo(f'chown -R root:root {supervisor_avail_dir}')
    sudo(f'chmod -R 755 {supervisor_avail_dir}')
    with cd(supervisor_enabled_dir):
        sudo(f'ln -sf {remotecfg}')
    sys_restart_service(c, 'supervisor')
    sudo(f'supervisorctl restart {domain}')
    sys_etc_git_commit(c, f'Setup Supervisor Config for Domain {domain}')



