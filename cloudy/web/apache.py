import os
from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port
from cloudy.sys.core import sys_reload_service

@task
def web_apache2_install(c: Connection):
    """Install apache2 and related modules."""
    c.sudo('apt -y install apache2')
    web_apache2_install_mods(c)
    util_apache2_bootstrap(c)
    sys_etc_git_commit(c, 'Installed apache2')

@task
def util_apache2_bootstrap(c: Connection):
    """Bootstrap Apache2 configuration from local templates."""
    c.sudo('rm -rf /etc/apache2/*')
    cfgdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../cfg'))

    configs = {
        'apache2/apache2.conf': '/etc/apache2/apache2.conf',
        'apache2/envvars.conf': '/etc/apache2/envvars',
        'apache2/ports.conf': '/etc/apache2/ports.conf'
    }

    for local, remote in configs.items():
        localcfg = os.path.expanduser(os.path.join(cfgdir, local))
        c.put(localcfg, remote, use_sudo=True)

    c.sudo('mkdir -p /etc/apache2/sites-available /etc/apache2/sites-enabled')

@task
def web_apache2_install_mods(c: Connection, py_version='3'):
    """Install apache2 related packages."""
    mod_wsgi = 'libapache2-mod-wsgi-py3' if '3' in py_version else 'libapache2-mod-wsgi'
    requirements = [mod_wsgi, 'libapache2-mod-rpaf']
    c.sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit(c, 'Installed apache2 and related packages')

@task
def web_apache2_set_port(c: Connection, port=''):
    """Setup Apache2 to listen to a new port."""
    remotecfg = '/etc/apache2/ports.conf'
    port = sys_show_next_available_port(c, port)
    c.sudo(f'echo "Listen 127.0.0.1:{port}" >> {remotecfg}')
    sys_reload_service(c, 'apache2')
    sys_etc_git_commit(c, f'Apache now listens on port {port}')

@task
def web_apache2_setup_domain(c: Connection, port: str, domain: str = ''):
    """Setup Apache2 config file for a domain."""
    apache_avail_dir = '/etc/apache2/sites-available'
    cfgdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../cfg'))
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/site.conf'))
    remotecfg = f'{apache_avail_dir}/{domain}'

    c.sudo(f'rm -rf {remotecfg}')
    c.put(localcfg, remotecfg, use_sudo=True)

    # Escape domain for sed replacement
    escaped_domain = domain.replace('.', r'\.')

    c.sudo(f'sed -i "s/port_num/{port}/g" {remotecfg}')
    c.sudo(f'sed -i "s/example\\.com/{escaped_domain}/g" {remotecfg}')

    c.sudo(f'chown -R root:root {apache_avail_dir}')
    c.sudo(f'chmod -R 755 {apache_avail_dir}')
    c.sudo(f'a2ensite {domain}')
    
    web_apache2_set_port(c, port)
    sys_reload_service(c, 'apache2')
    sys_etc_git_commit(c, f'Setup Apache Config for Domain {domain}')
