import os
import re
import sys

from fabric.api import run, sudo, cd, settings, hide
from fabric.contrib import files

def is_git_installed() -> bool:
    """Check if git is installed on the host."""
    with settings(warn_only=True):
        git = run('which git')
        return bool(git.strip())

def sys_etc_git_init() -> None:
    """Initialize git tracking in /etc if not already present."""
    if not is_git_installed():
        return
    if not files.exists('/etc/.git', use_sudo=True):
        with cd('/etc'):
            sudo('git init')
            sudo('git add .')
            sudo('git commit -a -m "Initial Submission"')

def sys_etc_git_commit(msg: str, print_only: bool = True) -> None:
    """
    Add/remove files from git and commit changes in /etc.
    If print_only is True or git is not installed, just print the message.
    """
    if print_only or not is_git_installed():
        print(msg)
        return

    sys_etc_git_init()
    with cd('/etc'):
        with settings(hide('warnings'), warn_only=True):
            sudo('git add .')
            sudo(f'git commit -a -m "{msg}"')



