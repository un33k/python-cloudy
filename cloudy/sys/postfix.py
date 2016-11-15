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
from fabric.api import cd
from fabric.contrib import files
from fabric.utils import abort

from cloudy.util.common import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit


def sys_install_postfix():
    """ Install postfix for outgoing email (loopback) - Ex: (cmd)"""
    sudo('echo \"postfix postfix/main_mailer_type select Internet Site\" | debconf-set-selections')
    sudo('echo \"postfix postfix/mailname string localhost\" | debconf-set-selections')
    sudo('echo \"postfix postfix/destinations string localhost.localdomain, localhost\" | debconf-set-selections')
    sudo('apt-get -y install postfix')
    sudo('/usr/sbin/postconf -e \"inet_interfaces = loopback-only\"')
    sys_etc_git_commit('Installed postfix on loopback for outgoing mail')
    sys_restart_service('postfix')

