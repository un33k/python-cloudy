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
from cloudy.db import *
from cloudy.sys import *


def srv_postgresql_server_setup():
    """ Update package repositories - Ex: (cmd)"""
    
    sys_update()
    sys_safe_upgrade()
    sys_install_common()
    sys_configure_timezone('Canada/Eastern')
    sys_git_configure('root', 'Val Neekman', 'val@neekware.com')
    sys_hostname_configure('nw-db1')
    sys_locale_configure()
    sys_install_postfix()
    sys_security_install_common()
    users = ['vman', 'admino']
    for user in users:
        sys_user_add(user)
        sys_user_add_sudoer(user)
        sys_user_add_to_group(user, 'www-data')
        sys_user_set_group_umask(user)
