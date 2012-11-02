import os
import re
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

def is_git_installed():
    """ Determin if git is installed on host """
    with settings(warn_only=True):
        git = run('which git')
        if git.strip():
            return True
    return False

def sys_etc_git_init():
    """ Track changes in /etc/ - Ex: (cmd) """
    
    if not is_git_installed():
        return
    if not files.exists('/etc/.git', use_sudo=True):
        with cd('/etc'):
            sudo('git init')
            sudo('git add .')
            sudo('git commit -a -m "Initial Submission"')

def sys_etc_git_commit(msg):
    """ Add/Remove files from git and commit changes - Ex: (cmd:<"some message">) """

    if not is_git_installed():
        return

    sys_etc_git_init()
    with cd('/etc'):
        with settings(warn_only=True):
            sudo('git add .')
            with settings(warn_only=True):
                sudo('git commit -a -m "{0}"'.format(msg))



