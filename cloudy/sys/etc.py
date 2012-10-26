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

def sys_etc_git_init():
    """ Track changes in /etc/ - Ex: (cmd) """

    if not files.exists('/etc/.git', use_sudo=True):
        with cd('/etc'):
            sudo('git init')
            sudo('git add .')
            sudo('git commit -a -m "Initial Submission"')

def sys_etc_git_commit(msg):
    """ Add/Remove files from git and commit changes - Ex: (cmd:<"some message">) """
    
    sys_etc_git_init()
    with cd('/etc'):
        with settings(warn_only=True):
            sudo('git add .')
            with settings(warn_only=True):
                sudo('git commit -a -m "{0}"'.format(msg))



