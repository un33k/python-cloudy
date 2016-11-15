import os
import re
import sys
import time

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.api import cd
from fabric.contrib import files
from fabric.utils import abort, warn

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port

def web_nginx_install():
    """ Install Nginx  - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'nginx',
    ])

    # install requirements
    sudo('apt-get -y install {}'.format(requirements))
    web_nginx_bootstrap()
    sudo('service nginx restart')
    sys_etc_git_commit('Installed Nginx')


def web_nginx_bootstrap():
    sudo('rm -rf /etc/nginx/*')
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'nginx/nginx.conf'))
    remotecfg = '/etc/nginx/nginx.conf'
    put(localcfg, remotecfg, use_sudo=True)

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'nginx/mime.types.conf'))
    remotecfg = '/etc/nginx/mime.types'
    put(localcfg, remotecfg, use_sudo=True)

    sudo('mkdir -p /etc/nginx/sites-available')
    sudo('mkdir -p /etc/nginx/sites-enabled')

def web_nginx_copy_ssl(domain, crt_dir='~/.ssh/certificates/'):
    """
    Move ssl certificate and key to the server.
    """
    sudo('mkdir -p /etc/ssl/nginx/crt/')
    sudo('mkdir -p /etc/ssl/nginx/key/')
    sudo('chmod -R 755 {}'.format('/etc/ssl/nginx/'))

    crt_dir = os.path.expanduser(crt_dir)
    if not os.path.exists(crt_dir):
        warn('local certificate dir not found: {}'.format(crt_dir))

    localcrt = os.path.expanduser(os.path.join(crt_dir, '{}.combo.crt'.format(domain)))
    remotecrtdir = '/etc/ssl/nginx/crt/{}.combo.crt'.format(domain)
    put(localcrt, remotecrtdir, use_sudo=True)

    localkey = os.path.expanduser(os.path.join(crt_dir, '{}.key'.format(domain)))
    remotekey = '/etc/ssl/nginx/key/{}.key'.format(domain)
    put(localkey, remotekey, use_sudo=True)

def web_nginx_setup_domain(domain, proto='http', port='', interface='*'):
    """ Setup Nginx config file for a domain - Ex: (cmd:<domain>,[protocol],[port])"""
    if 'https' in proto or 'ssl' in proto:
        proto = 'https'
        ssl_crt = '/etc/ssl/nginx/crt/{}.combo.crt'.format(domain)
        ssl_key = '/etc/ssl/nginx/key/{}.key'.format(domain)
        if not files.exists(ssl_crt, use_sudo=True) or not files.exists(ssl_key, use_sudo=True):
            warn('ssl certificate and key not found.\n{}\n{}'.format(ssl_crt, ssl_key))

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    nginx_avail_dir = '/etc/nginx/sites-available'
    nginx_enabled_dir = '/etc/nginx/sites-enabled'

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'nginx/{}.conf'.format(proto)))
    remotecfg = '{}/{}.{}'.format(nginx_avail_dir, proto, domain)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    if not port:
        port = sys_show_next_available_port()

    sudo('sed -i "s/port_num/{}/g" {}'.format(port, remotecfg))
    sudo('sed -i "s/public_interface/{}/g" {}'.format(interface, remotecfg))
    sudo('sed -i "s/example\.com/{}/g" {}'.format(domain.replace('.', '\.'), remotecfg))
    sudo('chown -R root:root {}'.format(nginx_avail_dir))
    sudo('chmod -R 755 {}'.format(nginx_avail_dir))
    with cd(nginx_enabled_dir):
        sudo('ln -sf {}'.format(remotecfg))
    time.sleep(2)
    sudo('service nginx reload')
    sys_etc_git_commit('Setup Nginx Config for Domain {}'.format(domain))






