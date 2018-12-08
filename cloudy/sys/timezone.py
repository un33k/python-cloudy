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

from cloudy.sys.etc import sys_etc_git_commit

def sys_time_install_common():
    """ Install common time / zone related - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'ntpdate',
    ])

    # install requirements
    sudo('apt -y install {}'.format(requirements))
    sys_configure_ntp()
    sys_etc_git_commit('Installed time / zone related system packages')


def sys_configure_timezone(zone='Canada/Eastern'):
    """ Configure system time zone - Ex: (cmd:<zone>) """
    zone = os.path.abspath(os.path.join('/usr/share/zoneinfo', zone))
    if files.exists(zone):
        sudo('ln -sf {} /etc/localtime'.format(zone))
        sys_etc_git_commit('Updated system timezone to ({})'.format(zone))
    else:
        print >> sys.stderr, 'Zone not found {}'.format(zone)


def sys_configure_ntp():
    """ Configure NTP - Ex: (cmd) """
    sudo('echo "59 23 * * * /usr/sbin/ntpdate ntp.ubuntu.com > /dev/null" | sudo tee -a /var/spool/cron/crontabs/root')







