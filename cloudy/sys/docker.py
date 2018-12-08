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
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_mkdir
from cloudy.util.common import sys_restart_service


def sys_docker_install():
    url = "https://download.docker.com/linux/ubuntu"
    sudo('curl -fsSL {}/gpg | apt-key add -'.format(url))
    sudo('add-apt-repository \"deb [arch=amd64] {} $(lsb_release -cs) stable\"'.format(url))
    sudo('apt update')
    sudo('apt -y install docker-ce')
    sudo('systemctl enable docker')
    sys_etc_git_commit('Installed docker (ce)')


def sys_docker_config():
    """ docker-server config - Ex: (cmd:)"""
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'docker/daemon.json'))
    remotecfg = '/etc/docker/daemon.json'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sys_mkdir('/docker')
    sys_etc_git_commit('Configured docker')
    sys_restart_service('docker')


def sys_docker_user_group(username):
    with settings(hide('warnings'), warn_only=True):
        sudo('groupadd docker')
    sudo('usermod -aG docker {}'.format(username))
