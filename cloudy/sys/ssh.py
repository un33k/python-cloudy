import os
from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_reload_service


@task
def sys_ssh_set_port(c: Connection, port: str = '22') -> None:
    """Set SSH port."""
    sshd_config = '/etc/ssh/sshd_config'
    c.sudo(f"sed -i 's/^#*Port .*/Port {port}/' {sshd_config}")
    sys_etc_git_commit(c, f'Configured ssh (Port={port})')
    sys_reload_service(c, 'ssh')


@task
def sys_ssh_disable_root_login(c: Connection) -> None:
    """Disable root login."""
    sshd_config = '/etc/ssh/sshd_config'
    c.sudo(f"sed -i 's/^#*PermitRootLogin .*/PermitRootLogin no/' {sshd_config}")
    c.sudo('passwd -l root')
    sys_etc_git_commit(c, 'Disabled root login')
    sys_reload_service(c, 'ssh')


@task
def sys_ssh_enable_root_login(c: Connection) -> None:
    """Enable root login."""
    sshd_config = '/etc/ssh/sshd_config'
    c.sudo(f"sed -i 's/^#*PermitRootLogin .*/PermitRootLogin yes/' {sshd_config}")
    sys_etc_git_commit(c, 'Enabled root login')
    sys_reload_service(c, 'ssh')


@task
def sys_ssh_enable_password_authentication(c: Connection) -> None:
    """Enable password authentication."""
    sshd_config = '/etc/ssh/sshd_config'
    c.sudo(f"sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication yes/' {sshd_config}")
    sys_etc_git_commit(c, 'Enable password authentication')
    sys_reload_service(c, 'ssh')


@task
def sys_ssh_disable_password_authentication(c: Connection) -> None:
    """Disable password authentication."""
    sshd_config = '/etc/ssh/sshd_config'
    c.sudo(f"sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication no/' {sshd_config}")
    sys_etc_git_commit(c, 'Disable password authentication')
    sys_reload_service(c, 'ssh')


@task
def sys_ssh_push_public_key(c: Connection, user: str, pub_key: str = '~/.ssh/id_rsa.pub') -> None:
    """Install a public key on the remote server for a user."""
    home_dir = '~' if user == 'root' else f'/home/{user}'
    ssh_dir = f'{home_dir}/.ssh'
    auth_key = f'{ssh_dir}/authorized_keys'
    pub_key = os.path.expanduser(pub_key)
    if not os.path.exists(pub_key):
        raise FileNotFoundError(f'Public key not found: {pub_key}')
    c.sudo(f'mkdir -p {ssh_dir}')
    c.put(pub_key, '/tmp/tmpkey')
    c.sudo(f'cat /tmp/tmpkey >> {auth_key}')
    c.sudo('rm -f /tmp/tmpkey')
    c.sudo(f'chown -R {user}:{user} {ssh_dir}')
    c.sudo(f'chmod 700 {ssh_dir}')
    c.sudo(f'chmod 600 {auth_key}')


@task
def sys_ssh_push_server_shared_keys(c: Connection, user: str, shared_dir: str = '~/.ssh/shared/ssh/') -> None:
    """Install shared SSH keys for a user (e.g., for GitHub access)."""
    home_dir = '~' if user == 'root' else f'/home/{user}'
    key_dir = os.path.expanduser(shared_dir)
    pri_key = os.path.join(key_dir, 'id_rsa')
    pub_key = os.path.join(key_dir, 'id_rsa.pub')
    for key in (pri_key, pub_key):
        if not os.path.exists(key):
            raise FileNotFoundError(f'Missing key file: {key}')
    remote_ssh_dir = f'{home_dir}/.ssh'
    c.sudo(f'mkdir -p {remote_ssh_dir}')
    c.put(pri_key, f'{remote_ssh_dir}/id_rsa')
    c.put(pub_key, f'{remote_ssh_dir}/id_rsa.pub')
    c.sudo(f'chown -R {user}:{user} {remote_ssh_dir}')
    c.sudo(f'chmod 700 {remote_ssh_dir}')
    c.sudo(f'chmod 600 {remote_ssh_dir}/id_rsa')
    c.sudo(f'chmod 644 {remote_ssh_dir}/id_rsa.pub')


