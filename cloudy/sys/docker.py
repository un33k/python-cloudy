import os
from fabric.api import sudo, put, settings, hide
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_mkdir
from cloudy.util.common import sys_restart_service


def sys_docker_install() -> None:
    """Install Docker CE on Ubuntu."""
    url = "https://download.docker.com/linux/ubuntu"
    sudo(f'curl -fsSL {url}/gpg | apt-key add -')
    sudo(f'add-apt-repository "deb [arch=amd64] {url} $(lsb_release -cs) stable"')
    sudo('apt update')
    sudo('apt -y install docker-ce')
    sudo('systemctl enable docker')
    sys_etc_git_commit('Installed docker (ce)')


def sys_docker_config() -> None:
    """Configure Docker daemon and create /docker directory."""
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'docker/daemon.json'))
    remotecfg = '/etc/docker/daemon.json'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    sys_mkdir('/docker')
    sys_etc_git_commit('Configured docker')
    sys_restart_service('docker')


def sys_docker_user_group(username: str) -> None:
    """Add a user to the docker group."""
    with settings(hide('warnings'), warn_only=True):
        sudo('groupadd docker')
    sudo(f'usermod -aG docker {username}')
