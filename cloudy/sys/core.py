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
    c.sudo(f'echo "{hostname}" > /etc/hostname')
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


# ============================================================================
# NEW INTUITIVE SYSTEM TASK ALIASES
# ============================================================================


@task(name="set-hostname")
@Context.wrap_context
def set_hostname(c: Context, name: str) -> None:
    """Set the system hostname.

    Args:
        name: New hostname for the system

    Example:
        fab -H myserver.com system.set-hostname --name=webserver01
    """
    sys_hostname_configure(c, name)


@task(name="update")
@Context.wrap_context
def update(c: Context) -> None:
    """Update package repositories.

    Example:
        fab -H myserver.com system.update
    """
    sys_update(c)


@task(name="upgrade")
@Context.wrap_context
def upgrade(c: Context, safe: bool = False) -> None:
    """Upgrade system packages.

    Args:
        safe: If true, performs safe upgrade with reboot

    Example:
        fab -H myserver.com system.upgrade --safe=true
    """
    if safe:
        sys_safe_upgrade(c)
    else:
        sys_upgrade(c)


@task(name="install-packages")
@Context.wrap_context
def install_packages(c: Context) -> None:
    """Install common system packages.

    Example:
        fab -H myserver.com system.install-packages
    """
    sys_install_common(c)


@task(name="set-locale")
@Context.wrap_context
def set_locale(c: Context, locale: str = "en_US.UTF-8") -> None:
    """Configure system locale.

    Args:
        locale: Locale to set (default: en_US.UTF-8)

    Example:
        fab -H myserver.com system.set-locale --locale=en_US.UTF-8
    """
    sys_locale_configure(c, locale)


@task(name="info")
@Context.wrap_context
def info(c: Context) -> None:
    """Show system information.

    Example:
        fab -H myserver.com system.info
    """
    sys_uname(c)


@task(name="restart")
@Context.wrap_context
def restart(c: Context) -> None:
    """Restart the system.

    Example:
        fab -H myserver.com system.restart
    """
    sys_shutdown(c, restart=True)


@task(name="shutdown")
@Context.wrap_context
def shutdown(c: Context) -> None:
    """Shutdown the system.

    Example:
        fab -H myserver.com system.shutdown
    """
    sys_shutdown(c, restart=False)


@task(name="add-host")
@Context.wrap_context
def add_host(c: Context, hostname: str, ip: str) -> None:
    """Add entry to /etc/hosts.

    Args:
        hostname: Hostname to add
        ip: IP address for hostname

    Example:
        fab -H myserver.com system.add-host --hostname=myapp.local --ip=127.0.0.1
    """
    sys_add_hosts(c, hostname, ip)


@task(name="configure-git")
@Context.wrap_context
def configure_git(c: Context, user: str, name: str, email: str) -> None:
    """Configure git for a user.

    Args:
        user: System username
        name: Git user full name
        email: Git user email

    Example:
        fab -H myserver.com system.configure-git --user=root --name="John Doe" \\
            --email=john@example.com
    """
    sys_git_configure(c, user, name, email)


# Service management aliases
@task(name="start-service")
@Context.wrap_context
def start_service(c: Context, name: str) -> None:
    """Start a system service.

    Args:
        name: Service name to start

    Example:
        fab -H myserver.com system.start-service --name=nginx
    """
    sys_start_service(c, name)


@task(name="stop-service")
@Context.wrap_context
def stop_service(c: Context, name: str) -> None:
    """Stop a system service.

    Args:
        name: Service name to stop

    Example:
        fab -H myserver.com system.stop-service --name=nginx
    """
    sys_stop_service(c, name)


@task(name="restart-service")
@Context.wrap_context
def restart_service(c: Context, name: str) -> None:
    """Restart a system service.

    Args:
        name: Service name to restart

    Example:
        fab -H myserver.com system.restart-service --name=nginx
    """
    sys_restart_service(c, name)


@task(name="reload-service")
@Context.wrap_context
def reload_service(c: Context, name: str) -> None:
    """Reload a system service.

    Args:
        name: Service name to reload

    Example:
        fab -H myserver.com system.reload-service --name=nginx
    """
    sys_reload_service(c, name)
