from fabric import task

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_set_default_editor(c: Context, default: int = 3) -> None:
    """
    Set the default editor using update-alternatives.
    :param default: The selection number for the editor
        (as shown by update-alternatives --config editor).
    """
    c.sudo(f"sh -c 'echo {default} | update-alternatives --config editor'")
    sys_etc_git_commit(c, f"Set default editor to ({default})")
