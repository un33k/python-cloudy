import os
from fabric.api import sudo, put
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port
from cloudy.util.common import sys_start_service, sys_reload_service

def web_apache_install():
    """Install apache2 and related modules."""
    sudo('apt -y install apache2')
    web_apache2_install_mods()
    util_apache2_bootstrap()
    sys_etc_git_commit(c, 'Installed apache2')

def util_apache2_bootstrap():
    """Bootstrap Apache2 configuration from local templates."""
    sudo('rm -rf /etc/apache2/*')
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')

    configs = {
        'apache2/apache2.conf': '/etc/apache2/apache2.conf',
        'apache2/envvars.conf': '/etc/apache2/envvars',
        'apache2/ports.conf': '/etc/apache2/ports.conf'
    }
    for local, remote in configs.items():
        localcfg = os.path.expanduser(os.path.join(cfgdir, local))
        put(localcfg, remote, use_sudo=True)

    sudo('mkdir -p /etc/apache2/sites-available')
    sudo('mkdir -p /etc/apache2/sites-enabled')

def web_apache2_install_mods(py_version='3'):
    """Install apache2 related packages."""
    mod_wsgi = 'libapache2-mod-wsgi-py3' if '3' in py_version else 'libapache2-mod-wsgi'
    requirements = [mod_wsgi, 'libapache2-mod-rpaf']
    sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit(c, 'Installed apache2 and related packages')

def web_apache2_set_port(port=''):
    """Setup Apache2 to listen to a new port."""
    remotecfg = '/etc/apache2/ports.conf'
    port = sys_show_next_available_port(port)
    sudo(f'echo "Listen 127.0.0.1:{port}" >> {remotecfg}')
    sys_reload_service(c, 'apache2')
    sys_etc_git_commit(c, f'Apache now listens on port {port}')

def web_apache2_setup_domain(domain, port):
    """Setup Apache2 config file for a domain."""
    apache_avail_dir = '/etc/apache2/sites-available'
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/site.conf'))
    remotecfg = f'{apache_avail_dir}/{domain}'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    sudo(f'sed -i "s/port_num/{port}/g" {remotecfg}')
    sudo(f'sed -i "s/example\\.com/{domain.replace(".", "\\.")}/g" {remotecfg}')
    sudo(f'chown -R root:root {apache_avail_dir}')
    sudo(f'chmod -R 755 {apache_avail_dir}')
    sudo(f'a2ensite {domain}')
    web_apache2_set_port(port)
    sys_reload_service(c, 'apache2')
    sys_etc_git_commit(c, f'Setup Apache Config for Domain {domain}')


