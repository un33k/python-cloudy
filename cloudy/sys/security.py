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

def sys_security_install_common() -> None:
    """Install common security applications."""
    requirements = [
        'fail2ban',
        'logcheck',
        'logcheck-database',
    ]
    sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit('Installed common security packages')




