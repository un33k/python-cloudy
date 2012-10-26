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

def sys_user_add(username):
    """ Add new user - Ex: (cmd:<user>)"""
    sudo('useradd --create-home --shell \"/bin/bash\" {0}'.format(username))
    sys_etc_git_commit('Added user({0})'.format(username))


def sys_user_add_sudoer(username):
    """ Add user to sudoers - Ex: (cmd:<user>)"""
    sudo('echo \"{0}   ALL=(ALL:ALL) ALL\" | sudo tee -a /etc/sudoers'.format(username))
    sys_etc_git_commit('Added user to sudoers - ({0})'.format(username))


def sys_user_remove_sudoer(username):
    """ Remove user from sudoer - Ex: (cmd:<user>)"""
    sudo('sed -i /\s*\{0}\s*.*/d {1}'.format(username, '/etc/sudoers'))
    sys_etc_git_commit('Removed user from sudoers - ({0})'.format(username))


def sys_user_add_to_group(username, group):
    """ Add user to existing group - Ex: (cmd:<user>,<group>)"""
    sudo('sudo usermod -a -G {0} {1}'.format(group, username))
    sys_etc_git_commit('Added user ({0}) to group ({1})'.format(username, group))


def sys_user_remove_from_group(username, group):
    """ Remove a user from a group - Ex: (cmd:<user>,<group>)"""
    sudo('sudo deluser {0} {1}'.format(username, group))
    sys_etc_git_commit('Removed user ({0}) from group ({1})'.format(username, group))


def sys_user_set_group_umask(username, umask='0002'):
    """ Set user umask - Ex: (cmd:<username>[umask])"""
    bashrc = '/home/{0}/.bashrc'.format(username)
    sudo('sed -i /\s*\umask\s*.*/d {0}'.format(bashrc))
    sudo('sed -i \'1iumask {0}\' {1}'.format(str(umask), bashrc))
    sys_etc_git_commit('Added umask ({0}) to user ({1})'.format(umask, username))





