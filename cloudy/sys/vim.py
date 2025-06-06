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
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit

def sys_set_default_editor(default: int = 3) -> None:
    """
    Set the default editor using update-alternatives.
    :param default: The selection number for the editor (as shown by update-alternatives --config editor).
    """
    sudo(f'echo {default} | update-alternatives --config editor')
    sys_etc_git_commit(f'Set default editor to ({default})')







