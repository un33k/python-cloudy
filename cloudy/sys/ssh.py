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
    files.sed(sshd_config, before='\s*#\s*Port\s*[0-9]*', after='Port {0}'.format(port), use_sudo=True)
    files.sed(sshd_config, before='\s*Port\s*[0-9]*', after='Port {0}'.format(port), use_sudo=True)
    sudo('service ssh reload')
    sys_etc_git_commit('Configured ssh (Port={0})'.format(port))


def sys_ssh_disable_root_login():
    """ Disable root login - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\PermitRootLogin\s*(yes|no)', after='PermitRootLogin no',use_sudo=True)
    files.sed(sshd_config, before='\s*PermitRootLogin\s*yes', after='PermitRootLogin no',use_sudo=True)
    sudo('sudo passwd -l root')
    sudo('service ssh reload')
    sys_etc_git_commit('Diabled root login')


def sys_ssh_enable_root_login():
    """ Enable root login - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\PermitRootLogin\s*(yes|no)', after='PermitRootLogin yes',use_sudo=True)
    files.sed(sshd_config, before='\s*PermitRootLogin\s*no', after='PermitRootLogin yes',use_sudo=True)
    sudo('service ssh reload')
    sys_etc_git_commit('Endabled root login')


def sys_ssh_enable_password_authentication():
    """ Enable password authentication - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\sPasswordAuthentication\s*(yes|no)', after='PasswordAuthentication yes',use_sudo=True)
    files.sed(sshd_config, before='\s*PasswordAuthentication\s*no', after='PasswordAuthentication yes',use_sudo=True)
    sudo('service ssh reload')
    sys_etc_git_commit('Enable password authentication')


def sys_ssh_disable_password_authentication():
    """ Diable password authentication - Ex: (cmd)"""
    sshd_config = '/etc/ssh/sshd_config'
    files.sed(sshd_config, before='\s*#\s*\sPasswordAuthentication\s*(yes|no)', after='PasswordAuthentication no',use_sudo=True)
    files.sed(sshd_config, before='\s*PasswordAuthentication\s*yes', after='PasswordAuthentication no',use_sudo=True)
    sudo('service ssh reload')
    sys_etc_git_commit('Disable password authentication')


def sys_ssh_push_public_key(user='', pub_key='~/.ssh/id_rsa.pub'):
    """ Install a public key on the remote server - Ex: (cmd:[user],[pub key])"""
    if not user:
        home_dir = '~'
    else:
        home_dir = '/home/{0}'.format(user)
        if not files.exists(home_dir):
            abort('Home directory not found for user: {0}'.format(user))

    pub_key = os.path.expanduser(pub_key)
    if not os.path.exists(pub_key):
        abort('Public key not found: {0}'.format(pub_key))

    put(pub_key, '/tmp/')
    sudo('sudo -u {0} mkdir -p {1}/.ssh'.format(user, home_dir))
    
    auth_key = '{0}/.ssh/authorized_keys'.format(home_dir)
    sudo('sudo -u {0} cat /tmp/{1} >> {2}'.format(user, os.path.basename(pub_key), auth_key))
    sudo('sudo rm -f /tmp/{1}'.format(user, os.path.basename(pub_key)))
    sudo('sudo chown {0}:{0} {1}'.format(user, auth_key))
    sudo('sudo -u {0} chmod 600 {1}'.format(user, auth_key))



