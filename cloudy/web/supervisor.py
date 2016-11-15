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
from cloudy.util.common import sys_restart_service


def web_supervisor_install():
    """ Install Supervisor  - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'supervisor',
    ])

    # install requirements
    sudo('apt-get -y install {}'.format(requirements))
    web_supervisor_bootstrap()
    sys_etc_git_commit('Installed Supervisor')


def web_supervisor_bootstrap():
    sudo('rm -rf /etc/supervisor/*')
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'supervisor/supervisord.conf'))
    remotecfg = '/etc/supervisor/supervisord.conf'

    put(localcfg, remotecfg, use_sudo=True)
    sudo('mkdir -p /etc/supervisor/sites-available')
    sudo('mkdir -p /etc/supervisor/sites-enabled')
    sudo('chown -R root:root /etc/supervisor')
    sudo('chmod -R 644 /etc/supervisor')
    sys_restart_service('supervisor')


def web_supervisor_setup_domain(domain, port, intrerface='0.0.0.0', worker_num=3):
    """ Setup Supervisor config file for a domain - Ex: (cmd:<domain>,[port])"""

    supervisor_avail_dir = '/etc/supervisor/sites-available'
    supervisor_enabled_dir = '/etc/supervisor/sites-enabled'

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'supervisor/site.conf'))
    remotecfg = '{}/{}.conf'.format(supervisor_avail_dir, domain)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    if not port:
        port = sys_show_next_available_port()
    sudo('sed -i "s/bound_address/{}/g" {}'.format(intrerface, remotecfg))
    sudo('sed -i "s/port_num/{}/g" {}'.format(port, remotecfg))
    sudo('sed -i "s/worker_num/{}/g" {}'.format(worker_num, remotecfg))
    sudo('sed -i "s/example\.com/{}/g" {}'.format(domain.replace('.', '\.'), remotecfg))
    sudo('chown -R root:root {}'.format(supervisor_avail_dir))
    sudo('chmod -R 755 {}'.format(supervisor_avail_dir))
    with cd(supervisor_enabled_dir):
        sudo('ln -sf {}'.format(remotecfg))
    sudo('service supervisor force-reload')
    sudo('supervisorctl restart {}'.format(domain))
    sys_etc_git_commit('Setup Supervisor Config for Domain {}'.format(domain))



