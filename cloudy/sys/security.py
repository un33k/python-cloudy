from fabric import task

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_security_install_common(c: Context) -> None:
    """Install common security applications."""
    requirements = [
        "fail2ban",
        "logcheck",
        "logcheck-database",
    ]
    c.sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit(c, "Installed common security packages")
