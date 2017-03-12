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
from cloudy.util.common import sys_start_service, sys_reload_service

def web_apache_install():
    """ Install apache2  - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'apache2',
    ])

    # install requirements
    sudo('apt -y install {}'.format(requirements))
    web_apache2_install_mods()
    util_apache2_bootstrap()
    sys_etc_git_commit('Installed apache2')


def util_apache2_bootstrap():
    sudo('rm -rf /etc/apache2/*')
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/apache2.conf'))
    remotecfg = '/etc/apache2/apache2.conf'
    put(localcfg, remotecfg, use_sudo=True)

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/envvars.conf'))
    remotecfg = '/etc/apache2/envvars'
    put(localcfg, remotecfg, use_sudo=True)

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/ports.conf'))
    remotecfg = '/etc/apache2/ports.conf'
    put(localcfg, remotecfg, use_sudo=True)

    sudo('mkdir -p /etc/apache2/sites-available')
    sudo('mkdir -p /etc/apache2/sites-enabled')

def web_apache2_install_mods(py_version='2.7'):
    """ Install apache2 related packages - Ex: (cmd)"""
    if '2' in py_version:
        mod_wsgi = 'libapache2-mod-wsgi'
    else:
        mod_wsgi = 'libapache2-mod-wsgi-py3'
    requirements = '%s' % ' '.join([
        mod_wsgi,
        'libapache2-mod-rpaf',
    ])

    # install requirements
    sudo('apt -y install {}'.format(requirements))
    sys_etc_git_commit('Installed apache2 and related packages')


def web_apache2_set_port(port=''):
    """ Setup Apache2 to listen to new port - Ex: (cmd:[port])"""

    remotecfg = '/etc/apache2/ports.conf'
    port = sys_show_next_available_port(port)
    sudo('echo \"Listen 127.0.0.1:{}\" >> {}'.format(port, remotecfg))
    sys_reload_service('apache2')
    sys_etc_git_commit('Apache now listens on port {}'.format(port))


def web_apache2_setup_domain(domain, port):
    """ Setup Apache2 config file for a domain - Ex: (cmd:<domain>,[port])"""

    apache_avail_dir = '/etc/apache2/sites-available'

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'apache2/site.conf'))
    remotecfg = '{}/{}'.format(apache_avail_dir, domain)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)

    sudo('sed -i "s/port_num/{}/g" {}'.format(port, remotecfg))
    sudo('sed -i "s/example\.com/{}/g" {}'.format(domain.replace('.', '\.'), remotecfg))
    sudo('chown -R root:root {}'.format(apache_avail_dir))
    sudo('chmod -R 755 {}'.format(apache_avail_dir))
    sudo('a2ensite {}'.format(domain))
    web_apache2_set_port(port)
    sys_reload_service('apache2')
    sys_etc_git_commit('Setup Apache Config for Domain {}'.format(domain))


