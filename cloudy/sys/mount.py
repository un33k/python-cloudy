import os
import re
import sys

from fabric.api import run, sudo, settings, hide
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit


def sys_mount_device_format(device: str, mount_point: str, filesystem: str = 'xfs') -> None:
    """Format and mount a device, ensuring it survives reboot."""

    if util_mount_is_mounted(device):
        abort(f'Device ({device}) is already mounted')
    util_mount_validate_vars(device, mount_point, filesystem)
    sudo(f'mkfs.{filesystem} -f {device}')
    sys_mount_device(device, mount_point, filesystem)
    sys_mount_fstab_add(device, mount_point, filesystem)
    sys_etc_git_commit(f'Mounted {device} on {mount_point} using {filesystem}')

def sys_mount_device(device: str, mount_point: str, filesystem: str = 'xfs') -> None:
    """Mount a device."""

    if util_mount_is_mounted(device):
        abort(f'Device ({device}) is already mounted')
    util_mount_validate_vars(device, mount_point, filesystem)
    sudo(f'mount -t {filesystem} {device} {mount_point}')

def sys_mount_fstab_add(device: str, mount_point: str, filesystem: str = 'xfs') -> None:
    """Add a mount record into /etc/fstab."""

    util_mount_validate_vars(device, mount_point, filesystem)
    entry = f"{device}  {mount_point}   {filesystem} noatime 0 0"
    sudo(f'echo "{entry}" | sudo tee -a /etc/fstab')

def util_mount_validate_vars(device: str, mount_point: str, filesystem: str = 'xfs') -> None:
    """Check system for device, mount point, and file system."""

    if not files.exists(mount_point):
        sudo(f'mkdir -p {mount_point}')
    if not files.exists(device):
        abort(f'Device ({device}) missing or not attached')

    if filesystem == 'xfs':
        sudo('apt-get install -y xfsprogs')

    sudo(f'grep -q {filesystem} /proc/filesystems || modprobe {filesystem}')

def util_mount_is_mounted(device: str) -> bool:
    """Check if a device is already mounted."""

    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        ret = run('df')
        return device in ret

