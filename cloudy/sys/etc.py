import os
import re
import sys
from operator import itemgetter

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.api import cd
from fabric.contrib import files

def etc_git_init():
    """ Track changes in /etc/ """

    if not files.exists('/etc/.git', use_sudo=True):
        with cd('/etc'):
            sudo('git init')
            sudo('git add .')
            sudo('git commit -a -m "Initial Submission"')

def etc_git_commit(msg):
    """ Add/Remove files from git and commit changes """
    
    etc_git_init()
    with cd('/etc'):
        sudo('git add .')
        with settings(warn_only=True):
            sudo('git commit -a -m "{0}"'.format(msg))



