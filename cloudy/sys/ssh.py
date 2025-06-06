import os
from fabric.api import run, sudo, put, settings
from fabric.contrib import files
from fabric.utils import abort, warn
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_reload_service


def sys_ssh_set_port(port: int = 22) -> None:
    """Set SSH port."""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before=r'\s*#\s*Port\s*[0-9]*', after=f'Port {port}', use_sudo=True)
    files.sed(sshd_config, before=r'\s*Port\s*[0-9]*', after=f'Port {port}', use_sudo=True)
    sys_etc_git_commit(f'Configured ssh (Port={port})')
    sys_reload_service('ssh')


def sys_ssh_disable_root_login() -> None:
    """Disable root login."""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before=r'\s*#\s*PermitRootLogin\s*(yes|no)', after='PermitRootLogin no', use_sudo=True)
    files.sed(sshd_config, before=r'\s*PermitRootLogin\s*yes', after='PermitRootLogin no', use_sudo=True)
    sudo('passwd -l root')
    sys_etc_git_commit('Disabled root login')
    sys_reload_service('ssh')


def sys_ssh_enable_root_login() -> None:
    """Enable root login."""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before=r'\s*#\s*PermitRootLogin\s*(yes|no)', after='PermitRootLogin yes', use_sudo=True)
    files.sed(sshd_config, before=r'\s*PermitRootLogin\s*no', after='PermitRootLogin yes', use_sudo=True)
    sys_etc_git_commit('Enabled root login')
    sys_reload_service('ssh')


def sys_ssh_enable_password_authentication() -> None:
    """Enable password authentication."""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before=r'\s*#\s*PasswordAuthentication\s*(yes|no)', after='PasswordAuthentication yes', use_sudo=True)
    files.sed(sshd_config, before=r'\s*PasswordAuthentication\s*no', after='PasswordAuthentication yes', use_sudo=True)
    sys_etc_git_commit('Enable password authentication')
    sys_reload_service('ssh')


def sys_ssh_disable_password_authentication() -> None:
    """Disable password authentication."""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before=r'\s*#\s*PasswordAuthentication\s*(yes|no)', after='PasswordAuthentication no', use_sudo=True)
    files.sed(sshd_config, before=r'\s*PasswordAuthentication\s*yes', after='PasswordAuthentication no', use_sudo=True)
    sys_etc_git_commit('Disable password authentication')
    sys_reload_service('ssh')


def sys_ssh_push_public_key(user: str, pub_key: str = '~/.ssh/id_rsa.pub') -> None:
    """Install a public key on the remote server for a user."""
    home_dir = '~' if user == 'root' else f'/home/{user}'
    if user != 'root' and not files.exists(home_dir):
        abort(f'Home directory not found for user: {user}')

    pub_key = os.path.expanduser(pub_key)
    if not os.path.exists(pub_key):
        abort(f'Public key not found: {pub_key}')

    ssh_dir = f'{home_dir}/.ssh'
    with settings(warn_only=True):
        sudo(f'mkdir -p {ssh_dir}')

    auth_key = f'{ssh_dir}/authorized_keys'
    tmp_key = f'/tmp/{os.path.basename(pub_key)}'
    sudo(f'rm -f {tmp_key}')
    put(pub_key, tmp_key)
    sudo(f'cat {tmp_key} >> {auth_key}')
    sudo(f'rm -f {tmp_key}')
    sudo(f'chown -R {user}:{user} {ssh_dir}')
    sudo(f'chmod 700 {ssh_dir}')
    sudo(f'chmod 600 {auth_key}')


def sys_ssh_push_server_shared_keys(user: str, shared_dir: str = '~/.ssh/shared/ssh/') -> None:
    """Install shared SSH keys for a user (e.g., for GitHub access)."""
    home_dir = '~' if user == 'root' else f'/home/{user}'
    if user != 'root' and not files.exists(home_dir):
        abort(f'Home directory not found for user: {user}')

    key_dir = os.path.expanduser(shared_dir)
    if not os.path.exists(key_dir):
        abort(f'Shared keys not found: {key_dir}')

    pri_key = os.path.join(key_dir, 'id_rsa')
    pub_key = os.path.join(key_dir, 'id_rsa.pub')

    for key in (pri_key, pub_key):
        if not os.path.exists(key):
            abort(f'Missing key file: {key}')

    remote_ssh_dir = f'{home_dir}/.ssh'
    with settings(warn_only=True):
        sudo(f'mkdir -p {remote_ssh_dir}')

    put(pri_key, remote_ssh_dir, use_sudo=True)
    put(pub_key, remote_ssh_dir, use_sudo=True)
    sudo(f'chown -R {user}:{user} {remote_ssh_dir}')
    sudo(f'chmod 700 {remote_ssh_dir}')
    sudo(f'chmod 600 {remote_ssh_dir}/id_rsa')
    sudo(f'chmod 644 {remote_ssh_dir}/id_rsa.pub')


