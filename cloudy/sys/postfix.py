import os
from fabric import Connection, task
from cloudy.util.common import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit


@task
def sys_install_postfix(c: Connection) -> None:
    """Install postfix for outgoing email (loopback only)."""
    selections = [
        'postfix postfix/main_mailer_type select Internet Site',
        'postfix postfix/mailname string localhost',
        'postfix postfix/destinations string localhost.localdomain, localhost'
    ]
    for sel in selections:
        c.sudo(f'echo "{sel}" | debconf-set-selections')
    c.sudo('apt -y install postfix')
    c.sudo('/usr/sbin/postconf -e "inet_interfaces = loopback-only"')
    sys_etc_git_commit(c, 'Installed postfix on loopback for outgoing mail')
    sys_restart_service(c, 'postfix')

