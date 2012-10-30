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

def util_get_connection():
    try:
        c = CloudyConfig()
        ACCESS_ID = c.cfg_grid['AWS']['access_id'].strip()
        SECRET_KEY = c.cfg_grid['AWS']['secret_key'].strip()
    except:
        abort('Unable to read ACCESS_ID, SECRET_KEY')

    Driver = get_driver(Provider.EC2)
    conn = Driver(ACCESS_ID, SECRET_KEY)
    return conn

def aws_list_instances():
    """ Lists all AWS EC2 instance - Ex: (cmd)"""
    conn = util_get_connection()
    nodes = conn.list_nodes()
    print >> sys.stderr, nodes
    return nodes


def aws_list_sizes():
    """ List node sizes """
    conn = util_get_connection()
    sizes = sorted([s for s in conn.list_sizes()])
    for s in sizes:
        print >> sys.stderr, ' - '.join([s.id, str(s.ram), str(s.price), s.driver.name])


def aws_get_size(size):
    """ Get Node Size """
    conn = util_get_connection()
    sizes = [s for s in conn.list_sizes()]
    if size:
        for s in sizes:
            if str(s.ram) == size or s.id == size:
                print >> sys.stderr, ' - '.join([s.id, str(s.ram), str(s.price), s.driver.name])
                return s
    
    return None

def aws_get_images():
    """ List available images """
    conn = util_get_connection()
    images = sorted([i for i in conn.list_images()])
    for i in images:
        print >> sys.stderr, ' - '.join([i.id, i.name, i.driver.name])


def aws_get_image(name):
    """ Confirm if a node exists """
    conn = util_get_connection()
    images = [i for i in conn.list_images()]
    if name:
        for i in images:
            if name == i.id:
                print >> sys.stderr, ' - '.join([i.id, i.name, i.driver.name])
                return i
    return None


def aws_get_locations():
    """ List available locations """
    conn = util_get_connection()
    locations = sorted([l for l in conn.list_locations()])
    for l in locations:
        print l
        # print >> sys.stderr, ' - '.join([i.id, i.name, i.driver.name])


def aws_create_node(name, image, size, security, key):
    """ Create a node """
    conn = util_get_connection()
    
    image = aws_get_image(image)
    if not image:
        abort('Invalid image ({0})'.format(image))

    size = aws_get_size(size)
    if not size:
        abort('Invalid size ({0})'.format(size))
        
    os.path.expanduser(f)
    node = conn.create_node(name=name, image=image, size=size, ex_securitygroup=securitygroup)
    if not node:
        abort('Failed to create node (name:{0}, image:{1}, size:{2})'.format(name, image, size))
    
    print >> sys.stderr, node
    return node




    