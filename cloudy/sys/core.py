import os
from typing import Optional
from fabric import Connection, task

from cloudy.sys.etc import sys_etc_git_commit

def _log_error(msg: str, exc: Exception) -> None:
    print(f"{msg}: {exc}")

@task
def sys_init(c: Connection) -> None:
    """Remove needrestart package if present (to avoid unnecessary restarts)."""
    c.sudo('apt remove -y needrestart', warn=True)

@task
def sys_update(c: Connection) -> None:
    """Update package repositories."""
    c.sudo('apt -y update')
    sys_etc_git_commit(c, 'Updated package repositories')

@task
def sys_upgrade(c: Connection) -> None:
    """Perform a full system upgrade and reboot."""
    c.sudo('apt install -y aptitude')
    c.sudo('apt update')
    c.sudo('DEBIAN_FRONTEND=noninteractive aptitude -y upgrade')
    sys_etc_git_commit(c, 'Upgraded the system')
    c.sudo('shutdown -r now')

@task
def sys_safe_upgrade(c: Connection) -> None:
    """Perform a safe system upgrade and reboot."""
    c.sudo('apt install -y aptitude')
    c.sudo('apt upgrade -y')
    c.sudo('DEBIAN_FRONTEND=noninteractive aptitude -y safe-upgrade')
    sys_etc_git_commit(c, 'Upgraded the system safely')
    c.sudo('shutdown -r now')

@task
def sys_git_install(c: Connection) -> None:
    """Install the latest version of git."""
    c.sudo('apt update')
    c.sudo('apt -y install git')

@task
def sys_install_common(c: Connection) -> None:
    """Install a set of common system utilities."""
    requirements = [
        'build-essential', 'gcc', 'subversion', 'mercurial', 'wget', 'vim', 'less', 'sudo',
        'redis-tools', 'curl', 'apt-transport-https', 'ca-certificates',
        'software-properties-common', 'net-tools', 'ntp'
    ]
    c.sudo(f'apt -y install {" ".join(requirements)}')

@task
def sys_git_configure(c: Connection, user: str, name: str, email: str) -> None:
    """Configure git for a given user."""
    c.sudo('apt install -y git-core')
    c.sudo(f'sudo -u {user} git config --global user.name "{name}"', warn=True)
    c.sudo(f'sudo -u {user} git config --global user.email "{email}"', warn=True)
    sys_etc_git_commit(c, f'Configured git for user: {user}')

@task
def sys_add_hosts(c: Connection, host: str, ip: str) -> None:
    """Add or update an entry in /etc/hosts."""
    host_file = '/etc/hosts'
    c.sudo(f"sed -i '/\\s*{host}\\s*.*/d' {host_file}")
    c.sudo(f"sed -i '1i{ip}\t{host}' {host_file}")
    sys_etc_git_commit(c, f'Added host:{host}, ip:{ip} to: {host_file}')

@task
def sys_hostname_configure(c: Connection, hostname: str) -> None:
    """Configure the system hostname."""
    c.sudo(f'echo "{hostname}" > /etc/hostname')
    c.sudo('hostname -F /etc/hostname')
    sys_etc_git_commit(c, f'Configured hostname to: {hostname}')

@task
def sys_locale_configure(c: Connection, locale: str = 'en_US.UTF-8') -> None:
    """Configure the system locale."""
    c.sudo('DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales')
    c.sudo(f'update-locale LANG={locale}')

@task
def sys_uname(c: Connection) -> None:
    """Display remote system information."""
    c.run('uname -a')

@task
def sys_show_process_by_memory_usage(c: Connection) -> None:
    """List processes by memory usage."""
    c.run('ps -eo pmem,pcpu,rss,vsize,args | sort -k 1 -r')

@task
def sys_show_disk_io(c: Connection) -> None:
    """List disk I/O statistics."""
    c.run('iostat -d -x 2 5')

@task
def sys_shutdown(c: Connection, restart: bool = True) -> None:
    """Shutdown or restart the host."""
    c.sudo('shutdown -r now' if restart else 'shutdown now')

@task
def sys_add_default_startup(c: Connection, program: str) -> None:
    """Enable a program to start at system boot."""
    c.sudo(f'systemctl enable {program}')

@task
def sys_remove_default_startup(c: Connection, program: str) -> None:
    """Disable a program from starting at system boot."""
    c.sudo(f'systemctl stop {program}', warn=True)
    c.sudo(f'systemctl disable {program}')

@task
def sys_mkdir(c: Connection, path: str = '', owner: str = '', group: str = '') -> Optional[str]:
    """Create a directory and optionally set owner/group."""
    if not path:
        return None
    path = os.path.abspath(path)
    try:
        c.sudo(f'mkdir -p "{path}"')
        if owner or group:
            chown_str = f"{owner}:{group}" if owner and group else owner or group
            c.sudo(f'chown {chown_str} "{path}"')
        return path
    except Exception as e:
        _log_error(f"Failed to create directory {path}", e)
        return None

@task
def sys_hold_package(c: Connection, package: str) -> None:
    """Prevent a package from being updated (hold the version)."""
    try:
        c.sudo(f'apt-mark hold {package}')
    except Exception as e:
        _log_error(f"Failed to hold package {package}", e)

@task
def sys_unhold_package(c: Connection, package: str) -> None:
    """Remove a package from being held at a version."""
    try:
        c.sudo(f'apt-mark unhold {package}')
    except Exception as e:
        _log_error(f"Failed to unhold package {package}", e)

@task
def sys_set_ipv4_precedence(c: Connection) -> None:
    """Set IPv4 to take precedence for sites that prefer it."""
    get_address_info_config = '/etc/gai.conf'
    pattern_before = r'\s*#\s*precedence\s*::ffff:0:0/96\s*100'
    pattern_after = 'precedence ::ffff:0:0/96 100'
    try:
        c.sudo(f"sed -i 's/{pattern_before}/{pattern_after}/' {get_address_info_config}")
    except Exception as e:
        _log_error("Failed to set IPv4 precedence", e)

def run_command(c: Connection, cmd: str, use_sudo: bool = False) -> Optional[str]:
    """Run a shell command, optionally with sudo, and handle errors."""
    try:
        result = c.sudo(cmd) if use_sudo else c.run(cmd)
        return result.stdout if hasattr(result, 'stdout') else str(result)
    except Exception as e:
        _log_error(f"Command failed: {cmd}", e)
        return None


