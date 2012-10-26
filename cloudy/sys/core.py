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
    """ Install common application """
    requirements = '%s' % ' '.join([
        'git',
        'subversion',
        'mercurial',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    
def sys_set_timezone(zone='Canada/Eastern'):
    """ Sets system time zone, given a zone location """
    zone = os.path.abspath(os.path.join('/usr/share/zoneinfo', zone))
    if files.exists(zone):
        sudo('ln -sf {0} /etc/localtime'.format(zone))
        sys_etc_git_commit('Updated system timezone to ({0})'.format(zone))
    else:
        print >> sys.stderr, 'Zone not found {0}'.format(zone)


def sys_make_swap_partition(size='512'):
    """ Ceates and install a swap file, given file size in MB """
    swap_file = '/swap/{0}MiB.swap'.format(size)
    sudo('mkdir -p /swap')
    if not files.exists(swap_file):
        sudo('fallocate -l {0}m {1}'.format(size, swap_file))
        sudo('chmod 600 {0}'.format(swap_file))
        sudo('mkswap {0}'.format(swap_file))
        sudo('swapon {0}'.format(swap_file))
        sudo('echo "{0} swap  swap  defaults  0 0" | sudo tee -a /etc/fstab'.format(swap_file))
        sys_etc_git_commit('Added swap file ({0})'.format(swap_file))
    else:
        print >> sys.stderr, 'Swap file ({0}) Exists'.format(swap_file)


def sys_mount_device(device='', filesystem='xfs', mount_point=''):
    """ Mounts a device given a mount point and filesystem type """
    if not mount_point:
        print >> sys.stderr, 'Mount point missing'
    if not device or not files.exists(device):
        print >> sys.stderr, 'Device missing or not attached'

    if filesystem == 'xfs':
        sudo('apt-get install -y xfsprogs')
    sudo('modprobe {0}'.format(filesystem))
    sudo('mkfs.{0} {1}'.format(filesystem, device))
    sudo('echo "{0}  {1}   {2} noatime 0 0" | sudo tee -a /etc/fstab'.format(device, mount_point, filesystem))
    sudo('mkdir -p {0}'.format(mount_point))
    sudo('mount -t {0} {1} {2}'.format(filesystem, device, mount_point))
    sys_etc_git_commit('Mounted {0} on {1} using {2}'.format(device, mount_point, filesystem))




