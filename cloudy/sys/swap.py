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

def sys_swap_configure(size: str = '512') -> None:
    """
    Create and install a swap file of the given size in MB.
    """
    swap_file = f'/swap/{size}MiB.swap'
    sudo('mkdir -p /swap')
    if not files.exists(swap_file):
        sudo(f'fallocate -l {size}m {swap_file}')
        sudo(f'chmod 600 {swap_file}')
        sudo(f'mkswap {swap_file}')
        sudo(f'swapon {swap_file}')
        sudo(f'echo "{swap_file} swap  swap  defaults  0 0" | sudo tee -a /etc/fstab')
        sys_etc_git_commit(f'Added swap file ({swap_file})')
    else:
        print(f'Swap file ({swap_file}) exists', file=sys.stderr)
