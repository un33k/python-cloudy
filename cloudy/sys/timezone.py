import os
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.api import cd
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit

def sys_time_install_common() -> None:
    """Install common time/zone related packages."""
    requirements = ['ntp', 'ntpdate']
    sudo(f'apt -y install {" ".join(requirements)}')
    sys_configure_ntp()
    sys_etc_git_commit('Installed time/zone related system packages')


def sys_configure_timezone(zone: str = 'Canada/Eastern') -> None:
    """Configure system time zone."""
    zone_path = os.path.abspath(os.path.join('/usr/share/zoneinfo', zone))
    if files.exists(zone_path):
        sudo(f'ln -sf {zone_path} /etc/localtime')
        sys_etc_git_commit(f'Updated system timezone to ({zone})')
    else:
        print(f'Zone not found {zone_path}', file=sys.stderr)


def sys_configure_ntp() -> None:
    """Configure NTP with a daily sync cron job."""
    cron_line = '59 23 * * * /usr/sbin/ntpdate ntp.ubuntu.com > /dev/null'
    sudo(f'echo "{cron_line}" | sudo tee -a /var/spool/cron/crontabs/root')







