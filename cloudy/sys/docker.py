import os

from fabric import task

from cloudy.sys.core import sys_mkdir, sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_docker_install(c: Context) -> None:
    """Install Docker CE on Ubuntu."""
    url = "https://download.docker.com/linux/ubuntu"
    c.sudo(f"sh -c 'curl -fsSL {url}/gpg | apt-key add -'")
    c.sudo(f'add-apt-repository "deb [arch=amd64] {url} $(lsb_release -cs) stable"')
    c.sudo("apt update")
    c.sudo("apt -y install docker-ce")
    c.sudo("systemctl enable docker")
    sys_etc_git_commit(c, "Installed docker (ce)")


@task
@Context.wrap_context
def sys_docker_config(c: Context) -> None:
    """Configure Docker daemon and create /docker directory."""
    cfgdir = os.path.join(os.path.dirname(__file__), "../cfg")
    localcfg = os.path.expanduser(os.path.join(cfgdir, "docker/daemon.json"))
    remotecfg = "/etc/docker/daemon.json"
    c.sudo(f"rm -rf {remotecfg}")
    c.put(localcfg, "/tmp/daemon.json")
    c.sudo(f"mv /tmp/daemon.json {remotecfg}")
    sys_mkdir(c, "/docker")
    sys_etc_git_commit(c, "Configured docker")
    sys_restart_service(c, "docker")


@task
@Context.wrap_context
def sys_docker_user_group(c: Context, username: str) -> None:
    """Add a user to the docker group."""
    # Try to create the group, ignore error if it exists
    c.sudo("groupadd docker", warn=True)
    c.sudo(f"usermod -aG docker {username}")
