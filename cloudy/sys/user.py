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
from fabric.utils import abort, warn

from cloudy.sys.etc import sys_etc_git_commit


def sys_user_delete(username):
    """ Delete new user - Ex: (cmd:<user>)"""
    with settings(warn_only=True):
        if username == 'root':
            warn('Cannot delete root user')
        sudo('pkill -KILL -u {}'.format(username))
        sudo('userdel {}'.format(username))
    sys_etc_git_commit('Deleted user({})'.format(username))


def sys_user_add(username):
    """ Add new user - Ex: (cmd:<user>)"""
    sys_user_delete(username)
    with settings(warn_only=True):
        sudo('useradd --create-home --shell \"/bin/bash\" {}'.format(username))
    sys_etc_git_commit('Added user({})'.format(username))


def sys_user_add_sudoer(username):
    """ Add user to sudoers - Ex: (cmd:<user>)"""
    sudo('echo \"{}   ALL=(ALL:ALL) ALL\" | sudo tee -a /etc/sudoers'.format(username))
    sys_etc_git_commit('Added user to sudoers - ({})'.format(username))


def sys_user_remove_sudoer(username):
    """ Remove user from sudoer - Ex: (cmd:<user>)"""
    sudo('sed -i /\s*{}\s*.*/d {}'.format(username, '/etc/sudoers'))
    sys_etc_git_commit('Removed user from sudoers - ({})'.format(username))


def sys_user_add_to_group(username, group):
    """ Add user to existing group - Ex: (cmd:<user>,<group>)"""
    with settings(warn_only=True):
        sudo('sudo usermod -a -G {} {}'.format(group, username))
    sys_etc_git_commit('Added user ({}) to group ({})'.format(username, group))


def sys_user_create_group(group):
    """ Create a new group - Ex: (cmd:<group>)"""
    with settings(warn_only=True):
        sudo('sudo addgroup {}'.format(group))
    sys_etc_git_commit('Created a new group ({})'.format(group))


def sys_user_remove_from_group(username, group):
    """ Remove a user from a group - Ex: (cmd:<user>,<group>)"""
    sudo('sudo deluser {} {}'.format(username, group))
    sys_etc_git_commit('Removed user ({}) from group ({})'.format(username, group))


def sys_user_set_group_umask(username, umask='0002'):
    """ Set user umask - Ex: (cmd:<username>[umask])"""
    bashrc = '/home/{}/.bashrc'.format(username)
    sudo('sed -i /\s*umask\s*.*/d {}'.format(bashrc))
    sudo('sed -i \'1iumask {}\' {}'.format(str(umask), bashrc))
    sys_etc_git_commit('Added umask ({}) to user ({})'.format(umask, username))


def sys_user_change_password(username, password):
    """ Change password for a user - Ex: (cmd:<user>,<password>)"""
    sudo('sudo echo "{}:{}" | chpasswd'.format(username, password))
    sys_etc_git_commit('Password changed for user ({})'.format(username))


def sys_user_set_pip_cache_dir(username):
    """ Set cache dir for pip for a given user - Ex: (cmd:<user>)"""
    bashrc = '/home/{}/.bashrc'.format(username)
    cache_dir = '/srv/www/.pip_cache_dir'
    sudo('mkdir -p {}'.format(cache_dir))
    sudo('chown -R :www-data {}'.format(cache_dir))
    sudo('chmod -R ug+wrx {}'.format(cache_dir))
    sudo('sed -i /\s*PIP_DOWNLOAD_CACHE\s*.*/d {}'.format(bashrc))
    sudo('sed -i \'1iexport PIP_DOWNLOAD_CACHE={}\' {}'.format(cache_dir, bashrc))





