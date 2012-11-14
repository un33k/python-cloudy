import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.api import cd
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.ports import sys_show_next_available_port

def web_nginx_install():
    """ Install Nginx  - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'nginx',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    util_nginx_bootstrap()
    sudo('service nginx restart')
    sys_etc_git_commit('Installed Nginx')


def util_nginx_bootstrap():
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'nginx/nginx.conf'))
    remotecfg = '/etc/nginx/nginx.conf'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sudo('rm -f /etc/nginx/sites-enabled/*default*')


def web_nginx_setup_domain(domain, proto='http', port=''):
    """ Setup Nginx config file for a domain - Ex: (cmd:<domain>,[protocol],[port])"""
    if 'https' in proto or 'ssl' in proto:
        proto = 'https'
        ssl_crt = '/etc/ssl/certs/{0}.crt'.format(domain)
        ssl_key = '/etc/ssl/private/{0}.key'.format(domain)
        if not files.exists(ssl_crt, use_sudo=True) or not files.exists(ssl_key, use_sudo=True):
            abort('ssl certificate and key not found.\n{0}\n{1}'.format(ssl_crt, ssl_key))

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'nginx/{0}.conf'.format(proto)))
    remotecfg = '/etc/nginx/conf.d/{0}.{1}.conf'.format(proto, domain)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    port = sys_show_next_available_port(port)
    sudo('sed -i "s/port_num/{0}/g" {1}'.format(port, remotecfg))
    sudo('sed -i "s/example\.com/{0}/g" {1}'.format(domain.replace('.', '\.'), remotecfg))
    sudo('service nginx reload')
    sys_etc_git_commit('Setup Nginx Config for Domain {0}'.format(domain))






