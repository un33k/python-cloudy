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


def sys_user_create_with_setup(
    c: Context, user_name: str, password: str, groups: str, shared_key_dir: str = ""
) -> None:
    """
    Create a user with full setup including groups, sudoer, and SSH keys.

    Args:
        c: Fabric context
        user_name: Username to create
        password: Password for the user
        groups: Comma-separated list of groups to add user to
        shared_key_dir: Optional path to shared SSH keys directory
    """
    if not user_name or not password:
        return

    sys_user_add(c, user_name)
    sys_user_change_password(c, user_name, password)
    sys_user_add_sudoer(c, user_name)
    sys_user_set_group_umask(c, user_name)
    sys_user_create_groups(c, groups)
    sys_user_add_to_groups(c, user_name, groups)

    # Set up SSH keys if configured
    if shared_key_dir:
        # Import here to avoid circular imports
        from cloudy.sys import ssh

        ssh.sys_ssh_push_server_shared_keys(c, user_name, shared_key_dir)


def validate_user_config(username: str, password: str) -> None:
    """
    Validate user configuration values.

    Args:
        username: Username to validate
        password: Password to validate

    Raises:
        ValueError: If validation fails
    """
    if username and not password:
        raise ValueError(f"User '{username}' specified but password is missing")
