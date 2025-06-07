import os
from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_restart_service

@task
def web_nginx_install(c: Connection):
    """Install Nginx and bootstrap configuration."""
    c.sudo('apt -y install nginx')
    web_nginx_bootstrap(c)
    sys_restart_service(c, 'nginx')
    sys_etc_git_commit(c, 'Installed Nginx')

@task
def web_nginx_bootstrap(c: Connection):
    """Bootstrap Nginx configuration from local templates."""
    c.sudo('rm -rf /etc/nginx/*')
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')

    configs = {
        'nginx/nginx.conf': '/etc/nginx/nginx.conf',
        'nginx/mime.types.conf': '/etc/nginx/mime.types'
    }
    for local, remote in configs.items():
        localcfg = os.path.expanduser(os.path.join(cfgdir, local))
        c.put(localcfg, remote, use_sudo=True)

    c.sudo('mkdir -p /etc/nginx/sites-available')
    c.sudo('mkdir -p /etc/nginx/sites-enabled')

@task
def web_nginx_copy_ssl(c: Connection, domain: str, crt_dir: str = '~/.ssh/certificates/'):
    """Move SSL certificate and key to the server."""
    c.sudo('mkdir -p /etc/ssl/nginx/crt/')
    c.sudo('mkdir -p /etc/ssl/nginx/key/')
    c.sudo('chmod -R 755 /etc/ssl/nginx/')

    crt_dir = os.path.expanduser(crt_dir)
    if not os.path.exists(crt_dir):
        print(f'⚠️ Local certificate dir not found: {crt_dir}')
        return

    localcrt = os.path.join(crt_dir, f'{domain}.combo.crt')
    remotecrt = f'/etc/ssl/nginx/crt/{domain}.combo.crt'
    c.put(localcrt, remotecrt, use_sudo=True)

    localkey = os.path.join(crt_dir, f'{domain}.key')
    remotekey = f'/etc/ssl/nginx/key/{domain}.key'
    c.put(localkey, remotekey, use_sudo=True)

@task
def web_nginx_setup_domain(
    c: Connection,
    domain: str,
    proto: str = 'http',
    interface: str = '*',
    upstream_address: str = '',
    upstream_port: str = ''
):
    """Setup Nginx config file for a domain."""
    if 'https' in proto or 'ssl' in proto:
        proto = 'https'
        ssl_crt = f'/etc/ssl/nginx/crt/{domain}.combo.crt'
        ssl_key = f'/etc/ssl/nginx/key/{domain}.key'
        if not c.sudo(f'test -f {ssl_crt}', warn=True).ok or not c.sudo(f'test -f {ssl_key}', warn=True).ok:
            print(f'⚠️ SSL certificate and key not found.\n{ssl_crt}\n{ssl_key}')

    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    nginx_avail_dir = '/etc/nginx/sites-available'
    nginx_enabled_dir = '/etc/nginx/sites-enabled'

    localcfg = os.path.expanduser(os.path.join(cfgdir, f'nginx/{proto}.conf'))
