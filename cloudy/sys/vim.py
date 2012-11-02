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
from fabric.contrib import files

from cloudy.sys.etc import sys_etc_git_commit

def sys_set_default_editor(default=3):
    """ Set the default editor - Ex: (cmd:[editor])"""
    sudo('echo 3 | sudo update-alternatives --config editor')
    sys_etc_git_commit('Set to default editor to ({0})'.format(default))







