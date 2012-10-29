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






