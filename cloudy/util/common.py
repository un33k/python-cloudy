import os
import re
import sys
import time

from fabric.api import sudo

def sys_restart_service(service):
    sudo('service {} stop'.format(service))
    time.sleep(2)
    sudo('service {} start'.format(service))
    time.sleep(2)
