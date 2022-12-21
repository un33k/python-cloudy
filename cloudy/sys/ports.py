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
from fabric.utils import abort


def sys_show_next_available_port(start=''):
    """ Show the next available port - Ex: (cmd:[starting_port])"""

    port = eval(start) if start else 8181
    for count in range(50):
        with settings(
            hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            port_in_use = run('netstat -lt | grep :{}'.format(port))
            if port_in_use:
                port += 1
                continue
    print(port)
    return port
