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

def sys_make_swap_partition(size='512'):
    """ Ceates and install a swap file, given file size in MB - Ex (cmd:[Size-MB]) """
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
