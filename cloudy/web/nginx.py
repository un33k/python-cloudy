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


def web_nginx_setup_domain(domain):
    """ Setup Nginx config file for a domain - Ex: (cmd:<domain>)"""
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'nginx/domain.conf'))
    remotecfg = '/etc/nginx/conf.d/{0}.conf'.format(domain)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    port = 8181
    for count in range(50):
        with settings(
            hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            port_in_use = run('netstat -na | grep 127.0.0.1:{0}'.format(port))
            if port_in_use:
                port += 1
                continue
    sudo('sed -i "s/port_num/{0}/g" {1}'.format(port, remotecfg))
    sudo('sed -i "s/example\.com/{0}/g" {1}'.format(domain.replace('.', '\.'), remotecfg))
    sudo('service nginx reload')
    sys_etc_git_commit('Setup Nginx Config for Domain {0}'.format(domain))






