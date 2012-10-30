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
from libcloud.compute.types import NodeState

def util_get_state2string(state):
    compute_state_map = {
        NodeState.RUNNING: 'running',
        NodeState.REBOOTING: 'rebooting',
        NodeState.TERMINATED: 'terminated',
        NodeState.PENDING: 'pending',
        NodeState.UNKNOWN: 'unknown',
    }
    if state in compute_state_map:
        return compute_state_map[state]


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
    """ List node sizes - Ex: (cmd)"""
    conn = util_get_connection()
    sizes = sorted([i for i in conn.list_sizes()])
    for i in sizes:
        print >> sys.stderr, ' - '.join([i.id, str(i.ram), str(i.price)])


def aws_get_size(size):
    """ Get Node Size - Ex: (cmd:<size>)"""
    conn = util_get_connection()
    sizes = [i for i in conn.list_sizes()]
    if size:
        for i in sizes:
            if str(i.ram) == size or i.id == size:
                print >> sys.stderr, ' - '.join([i.id, str(i.ram), str(i.price)])
                return i
    
    return None


def aws_list_images():
    """ List available images - Ex: (cmd)"""
    conn = util_get_connection()
    images = sorted([i for i in conn.list_images()])
    for i in images:
        print >> sys.stderr, ' - '.join([i.id, i.name])


def aws_get_image(name):
    """ Confirm if a node exists - Ex: (cmd:<image>)"""
    conn = util_get_connection()
    images = [i for i in conn.list_images()]
    if name:
        for i in images:
            if name == i.id:
                print >> sys.stderr, ' - '.join([i.id, i.name])
                return i
    return None


def aws_list_locations():
    """ List available locations - Ex: (cmd) """
    conn = util_get_connection()
    locations = sorted([i for i in conn.list_locations()])
    for i in locations:
        print >> sys.stderr, ' - '.join([i.availability_zone.name, i.id, i.name, i.country])


def aws_get_location(name):
    """ Confirm if a location exists - Ex: (cmd:<location>)"""
    conn = util_get_connection()
    locations = sorted([i for i in conn.list_locations()])
    if name:
        for i in locations:
            if name == i.availability_zone.name:
                print >> sys.stderr, ' - '.join([i.availability_zone.name, i.id, i.name, i.country])
                return i
    return None


def aws_list_security_groups():
    """ List available security groups - Ex: (cmd)"""
    conn = util_get_connection()
    groups = sorted([i for i in conn.ex_list_security_groups()])
    for i in groups:
        print >> sys.stderr, i


def aws_get_security_group(name):
    """ Confirm if a security group exists - Ex: (cmd:<securitygroup>) """
    conn = util_get_connection()
    groups = sorted([i for i in conn.ex_list_security_groups()])
    if name:
        for i in groups:
            if i == name:
                print >> sys.stderr, i
                return i
    return None


def aws_list_nodes():
    conn = util_get_connection()
    nodes = sorted([i for i in conn.list_nodes()])
    for i in nodes:
        print >> sys.stderr, ' - '.join([i.name, util_get_state2string(i.state), str(i.public_ips)])

def aws_get_node(name):
    conn = util_get_connection()
    nodes = sorted([i for i in conn.list_nodes()])
    for i in nodes:
        if i.name == name:
            print >> sys.stderr, ' - '.join([i.name, util_get_state2string(i.state), str(i.public_ips)])
            return i
    return None

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




    