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

from cloudy.sys.etc import sys_etc_git_commit

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


def sys_configure_timezone(zone):
    """ Configure system time zone - Ex: (cmd:<zone>) """
    zone = os.path.abspath(os.path.join('/usr/share/zoneinfo', zone))
    if files.exists(zone):
        sudo('ln -sf {0} /etc/localtime'.format(zone))
        sys_etc_git_commit('Updated system timezone to ({0})'.format(zone))
    else:
        print >> sys.stderr, 'Zone not found {0}'.format(zone)


def sys_git_configure(user, name, email):
    """ Configure git for a given user - Ex: (cmd:<user>,<name>,<email>)"""
    sudo('apt-get install -y git-core')
    sudo('sudo -u {0} git config --global user.name \"{1}\"'.format(user, name))
    sudo('sudo -u {0} git config --global user.email \"{1}\"'.format(user, email))
    sys_etc_git_commit('Configured git for user: {0}'.format(user))


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
    sudo('uname -a')




