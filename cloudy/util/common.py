import os
import re
import sys
import time

from fabric.api import sudo
from fabric.api import settings

def sys_start_service(service):
    sudo('systemctl start {}'.format(service))

def sys_stop_service(service):
    sudo('systemctl stop {}'.format(service))

def sys_reload_service(service):
    sudo('systemctl reload {}'.format(service))

def sys_restart_service(service):
    with settings(warn_only=True):
        sys_stop_service(service)
    time.sleep(2)
    sys_start_service(service)
    time.sleep(2)
