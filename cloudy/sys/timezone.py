import os
import sys
from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit

@task
def sys_time_install_common(c: Connection) -> None:
    """Install common time/zone related packages."""
    requirements = ['ntp', 'ntpdate']
    c.sudo(f'apt -y install {" ".join(requirements)}')
    sys_configure_ntp(c)
    sys_etc_git_commit(c, 'Installed time/zone related system packages')

@task
def sys_configure_timezone(c: Connection, zone: str = 'Canada/Eastern') -> None:
    """Configure system time zone."""
    zone_path = os.path.abspath(os.path.join('/usr/share/zoneinfo', zone))
    result = c.run(f'test -e {zone_path}', warn=True)
    if result.ok:
        c.sudo(f'ln -sf {zone_path} /etc/localtime')
        sys_etc_git_commit(c, f'Updated system timezone to ({zone})')
    else:
        print(f'Zone not found {zone_path}', file=sys.stderr)

@task
def sys_configure_ntp(c: Connection) -> None:
    """Configure NTP with a daily sync cron job."""
    cron_line = '59 23 * * * /usr/sbin/ntpdate ntp.ubuntu.com > /dev/null'
    c.sudo(f'echo "{cron_line}" | sudo tee -a /var/spool/cron/crontabs/root')







