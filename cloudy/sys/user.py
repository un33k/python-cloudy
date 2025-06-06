import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo, settings
from fabric.api import put
from fabric.api import env
from fabric.api import hide
from fabric.contrib import files
from fabric.utils import abort, warn
from cloudy.sys.etc import sys_etc_git_commit


def sys_user_delete(username: str) -> None:
    """Delete a user (except root)."""
    if username == 'root':
        warn('Cannot delete root user')
        return
    with settings(warn_only=True):
        sudo(f'pkill -KILL -u {username}')
        sudo(f'userdel {username}')
    sys_etc_git_commit(f'Deleted user({username})')


def sys_user_add(username: str) -> None:
    """Add a new user, deleting any existing user with the same name."""
    sys_user_delete(username)
    with settings(warn_only=True):
        sudo(f'useradd --create-home --shell "/bin/bash" {username}')
    sys_etc_git_commit(f'Added user({username})')


def sys_user_add_sudoer(username: str) -> None:
    """Add user to sudoers."""
    sudo(f'echo "{username}   ALL=(ALL:ALL) ALL" | sudo tee -a /etc/sudoers')
    sys_etc_git_commit(f'Added user to sudoers - ({username})')


def sys_user_remove_sudoer(username: str) -> None:
    """Remove user from sudoers."""
    sudo(f"sed -i '/\\s*{username}\\s*.*/d' /etc/sudoers")
    sys_etc_git_commit(f'Removed user from sudoers - ({username})')


def sys_user_add_to_group(username: str, group: str) -> None:
    """Add user to an existing group."""
    with settings(warn_only=True):
        sudo(f'usermod -a -G {group} {username}')
    sys_etc_git_commit(f'Added user ({username}) to group ({group})')


def sys_user_add_to_groups(username: str, groups: str) -> None:
    """Add user to multiple groups (comma-separated)."""
    for group in [g.strip() for g in groups.split(',') if g.strip()]:
        sys_user_add_to_group(username, group)


def sys_user_create_group(group: str) -> None:
    """Create a new group."""
    with settings(warn_only=True):
        sudo(f'addgroup {group}')
    sys_etc_git_commit(f'Created a new group ({group})')


def sys_user_create_groups(groups: str) -> None:
    """Create multiple groups (comma-separated)."""
    for group in [g.strip() for g in groups.split(',') if g.strip()]:
        sys_user_create_group(group)


def sys_user_remove_from_group(username: str, group: str) -> None:
    """Remove a user from a group."""
    sudo(f'deluser {username} {group}')
    sys_etc_git_commit(f'Removed user ({username}) from group ({group})')


def sys_user_set_group_umask(username: str, umask: str = '0002') -> None:
    """Set user umask in .bashrc."""
    bashrc = f'/home/{username}/.bashrc'
    sudo(f"sed -i '/\\s*umask\\s*.*/d' {bashrc}")
    sudo(f"sed -i '1iumask {umask}' {bashrc}")
    sys_etc_git_commit(f'Added umask ({umask}) to user ({username})')


def sys_user_change_password(username: str, password: str) -> None:
    """Change password for a user."""
    sudo(f'echo "{username}:{password}" | chpasswd')
    sys_etc_git_commit(f'Password changed for user ({username})')


def sys_user_set_pip_cache_dir(username: str) -> None:
    """Set cache dir for pip for a given user."""
    bashrc = f'/home/{username}/.bashrc'
    cache_dir = '/srv/www/.pip_cache_dir'
    sudo(f'mkdir -p {cache_dir}')
    sudo(f'chown -R :www-data {cache_dir}')
    sudo(f'chmod -R ug+wrx {cache_dir}')
    sudo(f"sed -i '/\\s*PIP_DOWNLOAD_CACHE\\s*.*/d' {bashrc}")
    sudo(f"sed -i '1iexport PIP_DOWNLOAD_CACHE={cache_dir}' {bashrc}")





