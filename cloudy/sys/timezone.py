import os
import sys

from fabric import task

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_time_install_common(c: Context) -> None:
    """Install common time/zone related packages."""
    requirements = ["ntpsec", "ntpdate"]
    c.sudo(f'apt -y install {" ".join(requirements)}')
    sys_configure_ntp(c)
    sys_etc_git_commit(c, "Installed time/zone related system packages")


@task
@Context.wrap_context
def sys_configure_timezone(c: Context, zone: str = "Canada/Eastern") -> None:
    """Configure system time zone."""
    zone_path = os.path.abspath(os.path.join("/usr/share/zoneinfo", zone))
    result = c.run(f"test -e {zone_path}", warn=True)
    if result.ok:
        c.sudo(f"ln -sf {zone_path} /etc/localtime")
        sys_etc_git_commit(c, f"Updated system timezone to ({zone})")
    else:
        print(f"Zone not found {zone_path}", file=sys.stderr)


@task
@Context.wrap_context
def sys_configure_ntp(c: Context) -> None:
    """Configure NTP with a daily sync cron job."""
    cron_line = "59 23 * * * /usr/sbin/ntpdate ntp.ubuntu.com > /dev/null"
    c.sudo(f"sh -c 'echo \"{cron_line}\" >> /var/spool/cron/crontabs/root'")
