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






