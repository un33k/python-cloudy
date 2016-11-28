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


def sys_upgrade():
    """ Perform a upgrade - Ex: (cmd)"""
    sudo('apt-get update')
    sudo('DEBIAN_FRONTEND=noninteractive aptitude -y upgrade')
    sudo('shutdown -r now')
    sys_etc_git_commit('Upgraded the system')

def sys_safe_upgrade():
    """ Perform a safe upgrade - Ex: (cmd)"""
    sudo('apt-get upgrade')
    sudo('DEBIAN_FRONTEND=noninteractive aptitude -y safe-upgrade')
    sys_etc_git_commit('Upgraded the system safely')
    sudo('shutdown -r now')

def sys_git_install():
    """
    Install the latest version of git.
    """
    sudo('apt-get update')
    sudo('apt-get -y install git')

def sys_install_upstart():
    sudo('yes | apt-get -y install upstart')

def sys_install_common():
    """ Install common application - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'build-essential',
        'gcc',
        'subversion',
        'mercurial',
        'wget',
        'vim',
        'less',
        'sudo',
    ])

    # install requirements
    sudo('apt-get -y install {}'.format(requirements))
    sys_install_upstart()

def sys_git_configure(user, name, email):
    """ Configure git for a given user - Ex: (cmd:<user>,<name>,<email>)"""
    sudo('apt-get install -y git-core')
    with settings(warn_only=True):
        sudo('sudo -u {} git config --global user.name \"{}\"'.format(user, name))
        sudo('sudo -u {} git config --global user.email \"{}\"'.format(user, email))
        sys_etc_git_commit('Configured git for user: {}'.format(user))


def sys_add_hosts(host, ip):
    """ Add ip:host to /etc/hosts - Ex: (cmd:<host>,<ip>)"""
    host_file = '/etc/hosts'
    sudo('sed -i /\s*\{}\s*.*/d {}'.format(host, host_file))
    sudo('sed -i \'1i{}\t{}\' {}'.format(ip, host, host_file))
    sys_etc_git_commit('Added host:{}, ip:{} to: {}'.format(host, ip, host_file))


def sys_hostname_configure(hostname):
    """ Configure hostname for a machine - Ex: (cmd:<name>)"""
    sudo('echo {} > /etc/hostname'.format(hostname))
    sudo('hostname -F /etc/hostname')
    sys_etc_git_commit('Configured hostname to: {}'.format(hostname))


def sys_locale_configure(locale='en_US.UTF-8'):
    """ Configure system's locale - Ex: (cmd:<locale>)"""
    sudo('DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales')
    sudo('update-locale LANG={}'.format(locale))


def sys_uname():
    """ Remote system info - Ex: (cmd)"""
    run('uname -a')


def sys_show_process_by_memory_usage():
    """ List processes by memory usage """
    run('ps -eo pmem,pcpu,rss,vsize,args | sort -k 1 -r')

def sys_show_disk_io():
    """ List disk io """
    run('iostat -d -x 2 5')


def sys_shutdown(restart=True):
    """ Shutdown a host - Ex: (cmd:[restart])"""
    if restart:
        sudo('shutdown -r now')
    else:
        sudo('shutdown now')

def sys_add_default_startup(program):
    """ Add an applications to start at system startup - Ex: (cmd) """
    sudo('systemctl enable {}'.format(program))


def sys_remove_default_startup(program):
    """ Remove an applications from starting at system startup - Ex: (cmd) """
    with settings(warn_only=True):
        sudo('systemctl stop {}'.format(program))
    sudo('systemctl disable {}'.format(program))


def sys_mkdir(path='', owner='', group=''):
    """ Make directory - Ex: (cmd:<dir>,[owner],[group])"""

    if not path:
        return

    path = os.path.abspath(path)
    sudo('mkdir -p {}'.format(path))
    return path

def sys_hold_package(package):
    """ Prevent package from being updated. Hold the version - Ex: (cmd) """
    sudo('apt-mark hold {}'.format(package))

def sys_unhold_package(package):
    """ Remove a package from being hold at a version - Ex: (cmd) """
    sudo('apt-mark unhold {}'.format(package))

def sys_set_ipv4_precedence():
    """ Set IPv4 to precede for site where they prefer it = Ex: (cmd) """
    get_address_info_config = '/etc/gai.conf'
    pattern_before = '\s*#\s*\precedence\s*::ffff:0:0/96\s*100'
    pattern_after = 'precedence ::ffff:0:0/96 100'
    files.sed(get_address_info_config, before=pattern_before, after=pattern_after, use_sudo=True)


