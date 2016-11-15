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

def sys_ssh_set_port(port=22):
    """ Set ssh port - Ex: (cmd:[port])"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*Port\s*[0-9]*', after='Port {}'.format(port), use_sudo=True)
    files.sed(sshd_config, before='\s*Port\s*[0-9]*', after='Port {}'.format(port), use_sudo=True)
    sys_etc_git_commit('Configured ssh (Port={})'.format(port))
    sudo('service ssh reload')


def sys_ssh_disable_root_login():
    """ Disable root login - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\PermitRootLogin\s*(yes|no)', after='PermitRootLogin no',use_sudo=True)
    files.sed(sshd_config, before='\s*PermitRootLogin\s*yes', after='PermitRootLogin no',use_sudo=True)
    sudo('sudo passwd -l root')
    sys_etc_git_commit('Diabled root login')
    sudo('service ssh reload')


def sys_ssh_enable_root_login():
    """ Enable root login - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\PermitRootLogin\s*(yes|no)', after='PermitRootLogin yes',use_sudo=True)
    files.sed(sshd_config, before='\s*PermitRootLogin\s*no', after='PermitRootLogin yes',use_sudo=True)
    sys_etc_git_commit('Endabled root login')
    sudo('service ssh reload')


def sys_ssh_enable_password_authentication():
    """ Enable password authentication - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\sPasswordAuthentication\s*(yes|no)', after='PasswordAuthentication yes',use_sudo=True)
    files.sed(sshd_config, before='\s*PasswordAuthentication\s*no', after='PasswordAuthentication yes',use_sudo=True)
    sys_etc_git_commit('Enable password authentication')
    sudo('service ssh reload')


def sys_ssh_disable_password_authentication():
    """ Diable password authentication - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\sPasswordAuthentication\s*(yes|no)', after='PasswordAuthentication no',use_sudo=True)
    files.sed(sshd_config, before='\s*PasswordAuthentication\s*yes', after='PasswordAuthentication no',use_sudo=True)
    sys_etc_git_commit('Disable password authentication')
    sudo('service ssh reload')


def sys_ssh_push_public_key(user, pub_key='~/.ssh/id_rsa.pub'):
    """ Install a public key on the remote server - Ex: (cmd:<user>,[pub key])"""
    if user == 'root':
        home_dir = '~'
    else:
        home_dir = '/home/{}'.format(user)
        if not files.exists(home_dir):
            abort('Home directory not found for user: {}'.format(user))

    pub_key = os.path.expanduser(pub_key)
    if not os.path.exists(pub_key):
        abort('Public key not found: {}'.format(pub_key))

    ssh_dir = '{}/.ssh'.format(home_dir)
    with settings(warn_only=True):
        sudo('mkdir -p {}'.format(ssh_dir))

    auth_key = '{}/authorized_keys'.format(ssh_dir)
    sudo('rm -f /tmp/{}'.format(os.path.basename(pub_key)))
    put(pub_key, '/tmp/')
    sudo('cat /tmp/{} >> {}'.format(os.path.basename(pub_key), auth_key))
    sudo('rm -f /tmp/{}'.format(os.path.basename(pub_key)))
    sudo('chown -R {}:{} {}'.format(user, user, ssh_dir))
    sudo('chmod -R 700 {}'.format(ssh_dir))


def sys_ssh_push_server_shared_keys(user, shared_dir='~/.ssh/shared/ssh/'):
    """ Install a shared keys on the remote server so all servers have access to github/bitbuket - Ex: (cmd:<user>,<shared-dir>)"""
    if user == 'root':
        home_dir = '~'
    else:
        home_dir = '/home/{}'.format(user)
        if not files.exists(home_dir):
            abort('Home directory not found for user: {}'.format(user))

    key_dir = os.path.expanduser(shared_dir)
    if not os.path.exists(key_dir):
        abort('Shared keys not found: {}'.format(key_dir))

    pri_key = os.path.expanduser(os.path.join(key_dir, 'id_rsa'))
    pub_key = os.path.expanduser(os.path.join(key_dir, 'id_rsa.pub'))

    remote_ssh_dir = '{}/.ssh'.format(home_dir)
    with settings(warn_only=True):
        sudo('mkdir -p {}'.format(remote_ssh_dir))

    put(pri_key, remote_ssh_dir, use_sudo=True)
    put(pub_key, remote_ssh_dir, use_sudo=True)
    sudo('chown -R {}:{} {}'.format(user, user, remote_ssh_dir))
    sudo('chmod -R 700 {}'.format(remote_ssh_dir))


