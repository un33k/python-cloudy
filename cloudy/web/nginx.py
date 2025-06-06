import os
import time
from fabric.api import sudo, put, cd
from fabric.contrib import files
from fabric.utils import warn
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port
from cloudy.util.common import sys_start_service, sys_reload_service, sys_restart_service


def web_nginx_install():
    """Install Nginx and bootstrap configuration."""
    sudo('apt -y install nginx')
    web_nginx_bootstrap()
    sys_restart_service('nginx')
    sys_etc_git_commit('Installed Nginx')


def web_nginx_bootstrap():
    """Bootstrap Nginx configuration from local templates."""
    sudo('rm -rf /etc/nginx/*')
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    configs = {
        'nginx/nginx.conf': '/etc/nginx/nginx.conf',
        'nginx/mime.types.conf': '/etc/nginx/mime.types'
    }
    for local, remote in configs.items():
        localcfg = os.path.expanduser(os.path.join(cfgdir, local))
        put(localcfg, remote, use_sudo=True)

    sudo('mkdir -p /etc/nginx/sites-available')
    sudo('mkdir -p /etc/nginx/sites-enabled')


def web_nginx_copy_ssl(domain, crt_dir='~/.ssh/certificates/'):
    """Move SSL certificate and key to the server."""
    sudo('mkdir -p /etc/ssl/nginx/crt/')
    sudo('mkdir -p /etc/ssl/nginx/key/')
    sudo('chmod -R 755 /etc/ssl/nginx/')

    crt_dir = os.path.expanduser(crt_dir)
    if not os.path.exists(crt_dir):
        warn(f'Local certificate dir not found: {crt_dir}')

    localcrt = os.path.join(crt_dir, f'{domain}.combo.crt')
    remotecrt = f'/etc/ssl/nginx/crt/{domain}.combo.crt'
    put(localcrt, remotecrt, use_sudo=True)

    localkey = os.path.join(crt_dir, f'{domain}.key')
    remotekey = f'/etc/ssl/nginx/key/{domain}.key'
    put(localkey, remotekey, use_sudo=True)


def web_nginx_setup_domain(domain, proto='http', interface='*', upstream_address='', upstream_port=''):
    """Setup Nginx config file for a domain."""
    if 'https' in proto or 'ssl' in proto:
        proto = 'https'
        ssl_crt = f'/etc/ssl/nginx/crt/{domain}.combo.crt'
        ssl_key = f'/etc/ssl/nginx/key/{domain}.key'
        if not files.exists(ssl_crt, use_sudo=True) or not files.exists(ssl_key, use_sudo=True):
            warn(f'SSL certificate and key not found.\n{ssl_crt}\n{ssl_key}')

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    nginx_avail_dir = '/etc/nginx/sites-available'
    nginx_enabled_dir = '/etc/nginx/sites-enabled'

    localcfg = os.path.expanduser(os.path.join(cfgdir, f'nginx/{proto}.conf'))
    remotecfg = f'{nginx_avail_dir}/{proto}.{domain}'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)

    if upstream_address and upstream_port:
        sudo(f'sed -i "s/upstream_address/{upstream_address}/g" {remotecfg}')
        sudo(f'sed -i "s/upstream_port/{upstream_port}/g" {remotecfg}')

    sudo(f'sed -i "s/public_interface/{interface}/g" {remotecfg}')
    sudo(f'sed -i "s/example\\.com/{domain.replace(".", "\\.")}/g" {remotecfg}')
    sudo(f'chown -R root:root {nginx_avail_dir}')
    sudo(f'chmod -R 755 {nginx_avail_dir}')
    with cd(nginx_enabled_dir):
        sudo(f'ln -sf {remotecfg}')
    time.sleep(2)
    sys_reload_service('nginx')
    sys_etc_git_commit(f'Setup Nginx Config for Domain {domain}')






