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

def web_create_data_directory(web_dir='/srv/www'):
    """ Create a data directory for the web files """
    sudo('mkdir -p {0}'.format(web_dir))


def web_create_log_directory(log_dir='/srv/www/log'):
    """ Create a data directory for the web files """
    sudo('mkdir -p {0}'.format(log_dir))
    
