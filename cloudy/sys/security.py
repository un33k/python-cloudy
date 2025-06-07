from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit

@task
def sys_security_install_common(c: Connection) -> None:
    """Install common security applications."""
    requirements = [
        'fail2ban',
        'logcheck',
        'logcheck-database',
    ]
    c.sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit(c, 'Installed common security packages')




