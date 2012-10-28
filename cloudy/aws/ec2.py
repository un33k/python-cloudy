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
from fabric.utils import abort

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.conf import CloudyConfig

def aws_list_instances():
    """ Lists all AWS EC2 instance - Ex: (cmd)"""
    try:
        c = CloudyConfig()
        AWS_ACCESS_ID = c.cfg_grid['AWS']['aws_access_id'].strip()
        AWS_SECRET_KEY = c.cfg_grid['AWS']['aws_secret_key'].strip()
    except:
        abort('Unable to read AWS_ACCESS_ID, AWS_SECRET_KEY')
 
    Driver = get_driver(Provider.EC2)
    conn = Driver(AWS_ACCESS_ID, AWS_SECRET_KEY)
    nodes = conn.list_nodes()
    print >> sys.stderr, nodes
    return nodes


def aws_create_node(name, securitygroup, ami, size='t1.micro'):
    
    try:
        c = CloudyConfig()
        AWS_ACCESS_ID = c.cfg_grid['AWS']['aws_access_id'].strip()
        AWS_SECRET_KEY = c.cfg_grid['AWS']['aws_secret_key'].strip()
    except:
        abort('Unable to read AWS_ACCESS_ID, AWS_SECRET_KEY')

    Driver = get_driver(Provider.EC2_US_EAST)
    conn = Driver(AWS_ACCESS_ID, AWS_SECRET_KEY)
    
    image = [i for i in conn.list_images() if i.id == ami ][0]
    size = [s for s in conn.list_sizes() if s.id == size][0]
    node = conn.create_node(name=name, image=image, size=size, ex_securitygroup=securitygroup)
    if not node:
        abort('Failed to create node (name:{0}, image:{1}, size:{2})'.format(name, image, size))
    
    print >> sys.stderr, node
    return node






    