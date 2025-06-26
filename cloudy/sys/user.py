import sys

from fabric import task

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_user_delete(c: Context, username: str) -> None:
    """Delete a user (except root)."""
    if username == "root":
        print("Cannot delete root user", file=sys.stderr)
        return
    c.sudo(f"pkill -KILL -u {username}", warn=True)
    c.sudo(f"userdel {username}", warn=True)
    sys_etc_git_commit(c, f"Deleted user({username})")


@task
@Context.wrap_context
def sys_user_add(c: Context, username: str) -> None:
    """Add a new user, deleting any existing user with the same name."""
    sys_user_delete(c, username)
    c.sudo(f'useradd --create-home --shell "/bin/bash" {username}', warn=True)
    sys_etc_git_commit(c, f"Added user({username})")


@task
@Context.wrap_context
def sys_user_add_sudoer(c: Context, username: str) -> None:
    """Add user to sudoers."""
    c.sudo(f'echo "{username}   ALL=(ALL:ALL) ALL" | sudo tee -a /etc/sudoers')
    sys_etc_git_commit(c, f"Added user to sudoers - ({username})")


@task
@Context.wrap_context
def sys_user_remove_sudoer(c: Context, username: str) -> None:
    """Remove user from sudoers."""
    c.sudo(f"sed -i '/\\s*{username}\\s*.*/d' /etc/sudoers")
    sys_etc_git_commit(c, f"Removed user from sudoers - ({username})")


@task
@Context.wrap_context
def sys_user_add_to_group(c: Context, username: str, group: str) -> None:
    """Add user to an existing group."""
    c.sudo(f"usermod -a -G {group} {username}", warn=True)
    sys_etc_git_commit(c, f"Added user ({username}) to group ({group})")


@task
@Context.wrap_context
def sys_user_add_to_groups(c: Context, username: str, groups: str) -> None:
    """Add user to multiple groups (comma-separated)."""
    for group in [g.strip() for g in groups.split(",") if g.strip()]:
        sys_user_add_to_group(c, username, group)


@task
@Context.wrap_context
def sys_user_create_group(c: Context, group: str) -> None:
    """Create a new group."""
    c.sudo(f"addgroup {group}", warn=True)
    sys_etc_git_commit(c, f"Created a new group ({group})")


@task
@Context.wrap_context
def sys_user_create_groups(c: Context, groups: str) -> None:
    """Create multiple groups (comma-separated)."""
    for group in [g.strip() for g in groups.split(",") if g.strip()]:
        sys_user_create_group(c, group)


@task
@Context.wrap_context
def sys_user_remove_from_group(c: Context, username: str, group: str) -> None:
    """Remove a user from a group."""
    c.sudo(f"deluser {username} {group}")
    sys_etc_git_commit(c, f"Removed user ({username}) from group ({group})")


@task
@Context.wrap_context
def sys_user_set_group_umask(c: Context, username: str, umask: str = "0002") -> None:
    """Set user umask in .bashrc."""
    bashrc = f"/home/{username}/.bashrc"
    c.sudo(f"sed -i '/\\s*umask\\s*.*/d' {bashrc}")
    c.sudo(f"sed -i '1iumask {umask}' {bashrc}")
    sys_etc_git_commit(c, f"Added umask ({umask}) to user ({username})")


@task
@Context.wrap_context
def sys_user_change_password(c: Context, username: str, password: str) -> None:
    """Change password for a user."""
    c.sudo(f'echo "{username}:{password}" | chpasswd')
    sys_etc_git_commit(c, f"Password changed for user ({username})")


@task
@Context.wrap_context
def sys_user_set_pip_cache_dir(c: Context, username: str) -> None:
    """Set cache dir for pip for a given user."""
    bashrc = f"/home/{username}/.bashrc"
    cache_dir = "/srv/www/.pip_cache_dir"
    c.sudo(f"mkdir -p {cache_dir}")
    c.sudo(f"chown -R :www-data {cache_dir}")
    c.sudo(f"chmod -R ug+wrx {cache_dir}")
    c.sudo(f"sed -i '/\\s*PIP_DOWNLOAD_CACHE\\s*.*/d' {bashrc}")
    c.sudo(f"sed -i '1iexport PIP_DOWNLOAD_CACHE={cache_dir}' {bashrc}")


# ============================================================================
# NEW INTUITIVE USER TASK ALIASES
# ============================================================================


@task(name="create")
@Context.wrap_context
def create(c: Context, name: str, groups: str = None, sudo: bool = False) -> None:
    """Create a new user.

    Args:
        name: Username to create
        groups: Comma-separated list of groups to add user to
        sudo: Whether to give user sudo privileges

    Example:
        fab -H myserver.com user.create --name=john --groups=docker,www-data --sudo=true
    """
    sys_user_add(c, name)

    if groups:
        sys_user_add_to_groups(c, name, groups)

    if sudo:
        sys_user_add_sudoer(c, name)


@task(name="delete")
@Context.wrap_context
def delete(c: Context, name: str) -> None:
    """Delete a user.

    Args:
        name: Username to delete

    Example:
        fab -H myserver.com user.delete --name=john
    """
    sys_user_delete(c, name)


@task(name="set-password")
@Context.wrap_context
def set_password(c: Context, name: str, password: str) -> None:
    """Change password for a user.

    Args:
        name: Username
        password: New password

    Example:
        fab -H myserver.com user.set-password --name=john --password=newsecret123
    """
    sys_user_change_password(c, name, password)


@task(name="add-to-group")
@Context.wrap_context
def add_to_group(c: Context, name: str, group: str) -> None:
    """Add user to a group.

    Args:
        name: Username
        group: Group name

    Example:
        fab -H myserver.com user.add-to-group --name=john --group=docker
    """
    sys_user_add_to_group(c, name, group)


@task(name="add-to-groups")
@Context.wrap_context
def add_to_groups(c: Context, name: str, groups: str) -> None:
    """Add user to multiple groups.

    Args:
        name: Username
        groups: Comma-separated list of groups

    Example:
        fab -H myserver.com user.add-to-groups --name=john --groups=docker,www-data,staff
    """
    sys_user_add_to_groups(c, name, groups)


@task(name="grant-sudo")
@Context.wrap_context
def grant_sudo(c: Context, name: str) -> None:
    """Grant sudo privileges to user.

    Args:
        name: Username

    Example:
        fab -H myserver.com user.grant-sudo --name=john
    """
    sys_user_add_sudoer(c, name)


@task(name="revoke-sudo")
@Context.wrap_context
def revoke_sudo(c: Context, name: str) -> None:
    """Revoke sudo privileges from user.

    Args:
        name: Username

    Example:
        fab -H myserver.com user.revoke-sudo --name=john
    """
    sys_user_remove_sudoer(c, name)


@task(name="create-group")
@Context.wrap_context
def create_group(c: Context, name: str) -> None:
    """Create a new group.

    Args:
        name: Group name

    Example:
        fab -H myserver.com user.create-group --name=developers
    """
    sys_user_create_group(c, name)
