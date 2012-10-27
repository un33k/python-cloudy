import os
import re
import sys
from operator import itemgetter
import datetime

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.conf import CloudyConfig

def aws_list_instances(cfg="~/.cloudy"):
    c = CloudyConfig(filenames=cfg)
    
    try:
        AWS_ACCESS_ID = c.cfg_grid['AWS']['AWS_ACCESS_ID']
        AWS_SECRET_KEY = c.cfg_grid['AWS']['AWS_SECRET_KEY']
    except:
        return
    Driver = get_driver(Provider.EC2)
    conn = Driver(AWS_ACCESS_ID, AWS_SECRET_KEY)
    nodes = conn.list_nodes()
    print nodes




    