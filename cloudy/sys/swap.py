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

def sys_swap_configure(size='512'):
    """ Ceates and install a swap file, given file size in MB - Ex (cmd:[Size-MB]) """
    swap_file = '/swap/{}MiB.swap'.format(size)
    sudo('mkdir -p /swap')
    if not files.exists(swap_file):
        sudo('fallocate -l {}m {}'.format(size, swap_file))
        sudo('chmod 600 {}'.format(swap_file))
        sudo('mkswap {}'.format(swap_file))
        sudo('swapon {}'.format(swap_file))
        sudo('echo "{} swap  swap  defaults  0 0" | sudo tee -a /etc/fstab'.format(swap_file))
        sys_etc_git_commit('Added swap file ({})'.format(swap_file))
    else:
        print >> sys.stderr, 'Swap file ({}) Exists'.format(swap_file)
