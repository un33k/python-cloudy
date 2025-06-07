from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit

@task
def sys_mount_device_format(
    c: Connection, device: str, mount_point: str, filesystem: str = 'xfs'
) -> None:
    """Format and mount a device, ensuring it survives reboot."""

    if util_mount_is_mounted(c, device):
        raise RuntimeError(f'Device ({device}) is already mounted')
    util_mount_validate_vars(c, device, mount_point, filesystem)
    c.sudo(f'mkfs.{filesystem} -f {device}')
    sys_mount_device(c, device, mount_point, filesystem)
    sys_mount_fstab_add(c, device, mount_point, filesystem)
    sys_etc_git_commit(c, f'Mounted {device} on {mount_point} using {filesystem}')

@task
def sys_mount_device(
    c: Connection, device: str, mount_point: str, filesystem: str = 'xfs'
) -> None:
    """Mount a device."""

    if util_mount_is_mounted(c, device):
        raise RuntimeError(f'Device ({device}) is already mounted')
    util_mount_validate_vars(c, device, mount_point, filesystem)
    c.sudo(f'mount -t {filesystem} {device} {mount_point}')

@task
def sys_mount_fstab_add(
    c: Connection, device: str, mount_point: str, filesystem: str = 'xfs'
) -> None:
    """Add a mount record into /etc/fstab."""

    util_mount_validate_vars(c, device, mount_point, filesystem)
    entry = f"{device}  {mount_point}   {filesystem} noatime 0 0"
    c.sudo(f'echo "{entry}" | sudo tee -a /etc/fstab')

@task
def util_mount_validate_vars(
    c: Connection, device: str, mount_point: str, filesystem: str = 'xfs'
) -> None:
    """Check system for device, mount point, and file system."""

    # Check if mount point exists, create if not
    result = c.run(f'test -d {mount_point}', warn=True)
    if result.failed:
        c.sudo(f'mkdir -p {mount_point}')
    # Check if device exists
    result = c.run(f'test -e {device}', warn=True)
    if result.failed:
        raise RuntimeError(f'Device ({device}) missing or not attached')

    if filesystem == 'xfs':
        c.sudo('apt-get install -y xfsprogs')

    c.sudo(f'grep -q {filesystem} /proc/filesystems || modprobe {filesystem}')

@task
def util_mount_is_mounted(c: Connection, device: str) -> bool:
    """Check if a device is already mounted."""

    result = c.run('df', hide=True, warn=True)
    return device in result.stdout

