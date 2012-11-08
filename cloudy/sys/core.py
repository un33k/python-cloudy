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

def sys_update():
    """ Update package repositories - Ex: (cmd)"""
    sudo('apt-get -y update')
    sys_etc_git_commit('Updated package repositories')


def sys_safe_upgrade():
    """ Performe a safe upgrade - Ex: (cmd)"""
    sudo('aptitude -y safe-upgrade')
    sys_etc_git_commit('Upgraded the system safely')


def sys_install_common():
    """ Install common application - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'build-essential',
        'gcc',
        'git',
        'subversion',
        'mercurial',
        'wget',
        'vim',
        'less',
        'sudo',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    sys_etc_git_commit('Installed common system packages')


def sys_git_configure(user, name, email):
    """ Configure git for a given user - Ex: (cmd:<user>,<name>,<email>)"""
    sudo('apt-get install -y git-core')
    sudo('sudo -u {0} git config --global user.name \"{1}\"'.format(user, name))
    sudo('sudo -u {0} git config --global user.email \"{1}\"'.format(user, email))
    sys_etc_git_commit('Configured git for user: {0}'.format(user))


def sys_add_hosts(host, ip):
    """ Add ip:host to /etc/hosts - Ex: (cmd:<host>,<ip>)"""
    host_file = '/etc/hosts'
    sudo('sed -i /\s*\{0}\s*.*/d {1}'.format(host, host_file))
    sudo('sed -i \'1i{0}\t{1}\' {2}'.format(ip, host, host_file))
    sys_etc_git_commit('Added host:{0}, ip:{1} to: {2}'.format(host, ip, host_file))


def sys_hostname_configure(hostname):
    """ Configure hostname for a machine - Ex: (cmd:<name>)"""
    sudo('echo {0} > /etc/hostname'.format(hostname))
    sudo('hostname -F /etc/hostname')
    sys_etc_git_commit('Configured hostname to: {0}'.format(hostname))


def sys_locale_configure(locale='en_US.UTF-8'):
    """ Configure system's locale - Ex: (cmd:<locale>)"""
    sudo('dpkg-reconfigure locales')
    sudo('update-locale LANG={0}'.format(locale))


def sys_uname():
    """ Remote system info - Ex: (cmd)"""
    run('uname -a')


def sys_show_process_by_memory_usage():
    """ List processes by memory usage """
    run('ps -eo pmem,pcpu,rss,vsize,args | sort -k 1 -r')

def sys_show_disk_io():
    """ List disk io """
    run('iostat -d -x 2 5')






