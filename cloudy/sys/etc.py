import sys
from fabric import task
from cloudy.util.context import Context

@task
@Context.wrap_context
def is_git_installed(c: Context) -> bool:
    """Check if git is installed on the host."""
    result = c.run('which git', hide=True, warn=True)
    return bool(result.stdout.strip())

@task
@Context.wrap_context
def sys_etc_git_init(c: Context) -> None:
    """Initialize git tracking in /etc if not already present."""
    if not is_git_installed(c):
        return
    result = c.run('test -d /etc/.git', warn=True)
    if result.failed:
        with c.cd('/etc'):
            c.sudo('git init')
            c.sudo('git add .')
            c.sudo('git commit -a -m "Initial Submission"')

@task
@Context.wrap_context
def sys_etc_git_commit(c: Context, msg: str, print_only: bool = True) -> None:
    """
    Add/remove files from git and commit changes in /etc.
    If print_only is True or git is not installed, just print the message.
    """
    if print_only or not is_git_installed(c):
        print(msg)
        return

    sys_etc_git_init(c)
    with c.cd('/etc'):
        try:
            c.sudo('git add .')
            c.sudo(f'git commit -a -m "{msg}"', warn=True, hide=True)
        except Exception as e:
            print(f"Git commit failed: {e}", file=sys.stderr)



