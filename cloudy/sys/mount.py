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
from fabric.utils import abort
from fabric.contrib import files

from cloudy.sys.etc import sys_etc_git_commit


def sys_mount_device(device, mount_point, filesystem='xfs'):
    """ Mount a device which survice a reboot - Ex: (cmd:<device>,<mountpoint>,[filesystem]) """
    
    if files.exists(mount_point):
        sudo('mkdir -p {0}'.format(mount_point))
    if not files.exists(device):
        abort('Device ({0}) missing or not attached'.format(device))

    if filesystem == 'xfs':
        sudo('apt-get install -y xfsprogs')
    sudo('grep -q xfs /proc/filesystems || modprobe {0}'.format(filesystem))
    sudo('mkfs.{0} {1}'.format(filesystem, device))
    sudo('echo "{0}  {1}   {2} noatime 0 0" | sudo tee -a /etc/fstab'.format(device, mount_point, filesystem))
    sudo('mkdir -p {0}'.format(mount_point))
    sudo('mount -t {0} {1} {2}'.format(filesystem, device, mount_point))
    sys_etc_git_commit('Mounted {0} on {1} using {2}'.format(device, mount_point, filesystem))




