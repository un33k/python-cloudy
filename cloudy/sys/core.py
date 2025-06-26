import os
import time
from typing import Optional

from fabric import task

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_log_error(c: Context, msg: str, exc: Exception) -> None:
    print(f"{msg}: {exc}")


@task
@Context.wrap_context
def sys_start_service(c: Context, service: str) -> None:
    """Start a systemd service."""
    c.sudo(f"systemctl start {service}")


@task
@Context.wrap_context
def sys_stop_service(c: Context, service: str) -> None:
    """Stop a systemd service."""
    c.sudo(f"systemctl stop {service}")


@task
@Context.wrap_context
def sys_reload_service(c: Context, service: str) -> None:
    """Reload a systemd service."""
    c.sudo(f"systemctl reload {service}")


@task
@Context.wrap_context
def sys_restart_service(c: Context, service: str) -> None:
    """Restart a systemd service safely."""
    c.sudo(f"systemctl stop {service}", warn=True)
    time.sleep(2)
    c.sudo(f"systemctl start {service}")
    time.sleep(2)


@task
@Context.wrap_context
def sys_init(c: Context) -> None:
    """Remove needrestart package if present (to avoid unnecessary restarts)."""
    c.sudo("apt remove -y needrestart", warn=False)
    c.sudo("apt autoremove -y", warn=False)


@task
@Context.wrap_context
def sys_update(c: Context) -> None:
    """Update package repositories."""
    c.sudo("apt -y update")
    c.sudo("apt list --upgradable", warn=True)
    sys_etc_git_commit(c, "Updated package repositories")


@task
@Context.wrap_context
def sys_upgrade(c: Context) -> None:
    """Perform a full system upgrade and reboot."""
    c.sudo("apt install -y aptitude")
    c.sudo("apt update")
    c.sudo("DEBIAN_FRONTEND=noninteractive aptitude -y upgrade")
    sys_etc_git_commit(c, "Upgraded the system")
    c.sudo("shutdown -r now")


@task
@Context.wrap_context
def sys_safe_upgrade(c: Context) -> None:
    """Perform a safe system upgrade and reboot."""
    c.sudo("apt install -y aptitude")
    c.sudo("apt upgrade -y")
    c.sudo("DEBIAN_FRONTEND=noninteractive aptitude -y safe-upgrade")
    sys_etc_git_commit(c, "Upgraded the system safely")
    c.sudo("shutdown -r now")


@task
@Context.wrap_context
def sys_git_install(c: Context) -> None:
    """Install the latest version of git."""
    c.sudo("apt update")
    c.sudo("apt -y install git")


@task
@Context.wrap_context
def sys_install_common(c: Context) -> None:
    """Install a set of common system utilities."""
    requirements = [
        "build-essential",
        "gcc",
        "subversion",
        "mercurial",
        "wget",
        "vim",
        "less",
        "sudo",
        "redis-tools",
        "curl",
        "apt-transport-https",
        "ca-certificates",
        "software-properties-common",
        "net-tools",
        "ntpsec",
    ]
    c.sudo(f'apt -y install {" ".join(requirements)}')


@task
@Context.wrap_context
def sys_git_configure(c: Context, user: str, name: str, email: str) -> None:
    """Configure git for a given user."""
    c.sudo("apt install -y git-core")
    c.sudo(f'sudo -u {user} git config --global user.name "{name}"', warn=True)
    c.sudo(f'sudo -u {user} git config --global user.email "{email}"', warn=True)
    sys_etc_git_commit(c, f"Configured git for user: {user}")


@task
@Context.wrap_context
def sys_add_hosts(c: Context, host: str, ip: str) -> None:
    """Add or update an entry in /etc/hosts."""
    host_file = "/etc/hosts"
    c.sudo(f"sed -i '/\\s*{host}\\s*.*/d' {host_file}")
    c.sudo(f"sed -i '1i{ip}\t{host}' {host_file}")
    sys_etc_git_commit(c, f"Added host:{host}, ip:{ip} to: {host_file}")


@task
@Context.wrap_context
def sys_hostname_configure(c: Context, hostname: str) -> None:
    """Configure the system hostname."""
    c.sudo(f"sh -c 'echo {hostname} > /etc/hostname'")
    c.sudo("hostname -F /etc/hostname")
    sys_etc_git_commit(c, f"Configured hostname to: {hostname}")


@task
@Context.wrap_context
def sys_locale_configure(c: Context, locale: str = "en_US.UTF-8") -> None:
    """Configure the system locale."""
    c.sudo("DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales")
    c.sudo(f"update-locale LANG={locale}")


@task
@Context.wrap_context
def sys_uname(c: Context) -> None:
    """Display remote system information."""
    c.run("uname -a")


@task
@Context.wrap_context
def sys_show_process_by_memory_usage(c: Context) -> None:
    """List processes by memory usage."""
    c.run("ps -eo pmem,pcpu,rss,vsize,args | sort -k 1 -r")


@task
@Context.wrap_context
def sys_show_disk_io(c: Context) -> None:
    """List disk I/O statistics."""
    c.run("iostat -d -x 2 5")


@task
@Context.wrap_context
def sys_shutdown(c: Context, restart: bool = True) -> None:
    """Shutdown or restart the host."""
    c.sudo("shutdown -r now" if restart else "shutdown now")


@task
@Context.wrap_context
def sys_add_default_startup(c: Context, program: str) -> None:
    """Enable a program to start at system boot."""
    c.sudo(f"systemctl enable {program}")


@task
@Context.wrap_context
def sys_remove_default_startup(c: Context, program: str) -> None:
    """Disable a program from starting at system boot."""
    c.sudo(f"systemctl stop {program}", warn=True)
    c.sudo(f"systemctl disable {program}")


@task
@Context.wrap_context
def sys_mkdir(c: Context, path: str = "", owner: str = "", group: str = "") -> Optional[str]:
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
        sys_log_error(c, f"Failed to create directory {path}", e)
        return None


@task
@Context.wrap_context
def sys_hold_package(c: Context, package: str) -> None:
    """Prevent a package from being updated (hold the version)."""
    try:
        c.sudo(f"apt-mark hold {package}")
    except Exception as e:
        sys_log_error(c, f"Failed to hold package {package}", e)


@task
@Context.wrap_context
def sys_unhold_package(c: Context, package: str) -> None:
    """Remove a package from being held at a version."""
    try:
        c.sudo(f"apt-mark unhold {package}")
    except Exception as e:
        sys_log_error(c, f"Failed to unhold package {package}", e)


@task
@Context.wrap_context
def sys_set_ipv4_precedence(c: Context) -> None:
    """Set IPv4 to take precedence for sites that prefer it."""
    get_address_info_config = "/etc/gai.conf"
    # Use POSIX character class [[:space:]] instead of \s, and use # delimiter in sed.
    pattern_before = r"^[ \t]*#[ \t]*precedence[ \t]*::ffff:0:0/96[ \t]*100"
    pattern_after = "precedence ::ffff:0:0/96 100"
    try:
        # Use | delimiter in sed to avoid conflicts with # in the pattern
        sed_command = f'sed -i "s|{pattern_before}|{pattern_after}|" {get_address_info_config}'
        c.sudo(sed_command)
    except Exception as e:
        sys_log_error(c, "Failed to set IPv4 precedence", e)


@task
@Context.wrap_context
def run_command(c: Context, cmd: str, use_sudo: bool = False) -> Optional[str]:
    """Run a shell command, optionally with sudo, and handle errors."""
    try:
        result = c.sudo(cmd) if use_sudo else c.run(cmd)
        return result.stdout if hasattr(result, "stdout") else str(result)
    except Exception as e:
        sys_log_error(c, f"Command failed: {cmd}", e)
        return None
