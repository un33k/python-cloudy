import os
from typing import Optional

from fabric.api import run, sudo, settings
from fabric.contrib import files

from cloudy.sys.etc import sys_etc_git_commit

def _log_error(msg: str, exc: Exception) -> None:
    print(f"{msg}: {exc}")

def sys_init() -> None:
    """Remove needrestart package if present (to avoid unnecessary restarts)."""
    with settings(warn_only=True):
        sudo('apt remove -y needrestart')

def sys_update() -> None:
    """Update package repositories."""
    sudo('apt -y update')
    sys_etc_git_commit('Updated package repositories')

def sys_upgrade() -> None:
    """Perform a full system upgrade and reboot."""
    sudo('apt install -y aptitude')
    sudo('apt update')
    sudo('DEBIAN_FRONTEND=noninteractive aptitude -y upgrade')
    sys_etc_git_commit('Upgraded the system')
    sudo('shutdown -r now')

def sys_safe_upgrade() -> None:
    """Perform a safe system upgrade and reboot."""
    sudo('apt install -y aptitude')
    sudo('apt upgrade -y')
    sudo('DEBIAN_FRONTEND=noninteractive aptitude -y safe-upgrade')
    sys_etc_git_commit('Upgraded the system safely')
    sudo('shutdown -r now')

def sys_git_install() -> None:
    """Install the latest version of git."""
    sudo('apt update')
    sudo('apt -y install git')

def sys_install_common() -> None:
    """Install a set of common system utilities."""
    requirements = [
        'build-essential', 'gcc', 'subversion', 'mercurial', 'wget', 'vim', 'less', 'sudo',
        'redis-tools', 'curl', 'apt-transport-https', 'ca-certificates',
        'software-properties-common', 'net-tools', 'ntp'
    ]
    sudo(f'apt -y install {" ".join(requirements)}')

def sys_git_configure(user: str, name: str, email: str) -> None:
    """Configure git for a given user."""
    sudo('apt install -y git-core')
    with settings(warn_only=True):
        sudo(f'sudo -u {user} git config --global user.name "{name}"')
        sudo(f'sudo -u {user} git config --global user.email "{email}"')
    sys_etc_git_commit(f'Configured git for user: {user}')

def sys_add_hosts(host: str, ip: str) -> None:
    """Add or update an entry in /etc/hosts."""
    host_file = '/etc/hosts'
    sudo(f"sed -i '/\\s*{host}\\s*.*/d' {host_file}")
    sudo(f"sed -i '1i{ip}\t{host}' {host_file}")
    sys_etc_git_commit(f'Added host:{host}, ip:{ip} to: {host_file}')

def sys_hostname_configure(hostname: str) -> None:
    """Configure the system hostname."""
    sudo(f'echo "{hostname}" > /etc/hostname')
    sudo('hostname -F /etc/hostname')
    sys_etc_git_commit(f'Configured hostname to: {hostname}')

def sys_locale_configure(locale: str = 'en_US.UTF-8') -> None:
    """Configure the system locale."""
    sudo('DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales')
    sudo(f'update-locale LANG={locale}')

def sys_uname() -> None:
    """Display remote system information."""
    run('uname -a')

def sys_show_process_by_memory_usage() -> None:
    """List processes by memory usage."""
    run('ps -eo pmem,pcpu,rss,vsize,args | sort -k 1 -r')

def sys_show_disk_io() -> None:
    """List disk I/O statistics."""
    run('iostat -d -x 2 5')

def sys_shutdown(restart: bool = True) -> None:
    """Shutdown or restart the host."""
    sudo('shutdown -r now' if restart else 'shutdown now')

def sys_add_default_startup(program: str) -> None:
    """Enable a program to start at system boot."""
    sudo(f'systemctl enable {program}')

def sys_remove_default_startup(program: str) -> None:
    """Disable a program from starting at system boot."""
    with settings(warn_only=True):
        sudo(f'systemctl stop {program}')
    sudo(f'systemctl disable {program}')

def sys_mkdir(path: str = '', owner: str = '', group: str = '') -> Optional[str]:
    """Create a directory and optionally set owner/group."""
    if not path:
        return None
    path = os.path.abspath(path)
    try:
        sudo(f'mkdir -p "{path}"')
        if owner or group:
            chown_str = f"{owner}:{group}" if owner and group else owner or group
            sudo(f'chown {chown_str} "{path}"')
        return path
    except Exception as e:
        _log_error(f"Failed to create directory {path}", e)
        return None

def sys_hold_package(package: str) -> None:
    """Prevent a package from being updated (hold the version)."""
    try:
        sudo(f'apt-mark hold {package}')
    except Exception as e:
        _log_error(f"Failed to hold package {package}", e)

def sys_unhold_package(package: str) -> None:
    """Remove a package from being held at a version."""
    try:
        sudo(f'apt-mark unhold {package}')
    except Exception as e:
        _log_error(f"Failed to unhold package {package}", e)

def sys_set_ipv4_precedence() -> None:
    """Set IPv4 to take precedence for sites that prefer it."""
    get_address_info_config = '/etc/gai.conf'
    pattern_before = r'\s*#\s*precedence\s*::ffff:0:0/96\s*100'
    pattern_after = 'precedence ::ffff:0:0/96 100'
    try:
        files.sed(get_address_info_config, before=pattern_before, after=pattern_after, use_sudo=True)
    except Exception as e:
        _log_error("Failed to set IPv4 precedence", e)

def run_command(cmd: str, use_sudo: bool = False) -> Optional[str]:
    """Run a shell command, optionally with sudo, and handle errors."""
    try:
        result = sudo(cmd) if use_sudo else run(cmd)
        return result
    except Exception as e:
        _log_error(f"Command failed: {cmd}", e)
        return None


