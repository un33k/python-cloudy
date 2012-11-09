import os
import re
import sys
from operator import itemgetter
import datetime
import time

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
from libcloud.compute.base import Node

def util_print_node(node):
    if node:
        print >> sys.stderr, ', '.join([
                        'name: ' + node.name, 
                        'status: ' + util_get_state2string(node.state), 
                        'image: '  + node.extra['imageId'],
                        'zone: ' + node.extra['availability'],
                        'key: '  + node.extra['keyname'],
                        'size: ' + node.extra['instancetype'],
                        'pub ip: ' + str(node.public_ips)]
                    )

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


def util_wait_till_node(name, state, timeout=10):
    node = None
    elapsed = 0
    frequency = 5
    while elapsed < timeout:
        node = aws_get_node(name)
        if node:
            if node.state == state:
                break
        time.sleep(frequency)
        elapsed = elapsed + frequency
    return node

def util_wait_till_node_destroyed(name, timeout=15):
    return util_wait_till_node(name, NodeState.TERMINATED, timeout)


def util_wait_till_node_running(name, timeout=15):
    return util_wait_till_node(name, NodeState.RUNNING, timeout)


def util_list_instances():
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


def aws_security_group_found(name):
    """ Confirm if a security group exists - Ex: (cmd:<name>) """
    conn = util_get_connection()
    groups = sorted([i for i in conn.ex_list_security_groups()])
    if name:
        for i in groups:
            if i == name:
                print >> sys.stderr, i
                return True
    return False


def aws_list_keypairs():
    """ List all available keyparis - Ex: (cmd)"""
    conn = util_get_connection()
    nodes = sorted([i for i in conn.ex_describe_all_keypairs()])
    for i in nodes:
        print i


def aws_keypair_found(name):
    """ Confirm if a keypair exists - Ex: (cmd:<name>) """

    conn = util_get_connection()
    keys = sorted([i for i in conn.ex_describe_all_keypairs()])
    for i in keys:
        if i == name:
            print i
            return True

    return False


def aws_list_nodes():
    """ List all available computing nodes - Ex: (cmd)"""

    conn = util_get_connection()
    nodes = sorted([i for i in conn.list_nodes()])
    for i in nodes:
        util_print_node(i)


def aws_get_node(name):
    """ Confirm if a computing node exists - Ex: (cmd:<name>) """

    conn = util_get_connection()
    nodes = sorted([i for i in conn.list_nodes()])
    for i in nodes:
        if i.name == name:
            util_print_node(i)
            return i
    return None


def aws_create_node(name, image, size, security, key, timeout=30):
    """ Create a node - Ex: (cmd:<name>,<image>,<size>,[secuirty],[key],[timeout]) """
    conn = util_get_connection()

    if aws_get_node(name):
        abort('Node already exists ({0})'.format(name))

    size = aws_get_size(size)
    if not size:
        abort('Invalid size ({0})'.format(size))

    if not aws_security_group_found(security):
        abort('Invalid security group ({0})'.format(security))
        
    if not aws_keypair_found(key):
        abort('Invalid key ({0})'.format(key))

    image = aws_get_image(image)
    if not image:
        abort('Invalid image ({0})'.format(image))

    node = conn.create_node(name=name, image=image, size=size, ex_securitygroup=security, ex_keyname=key)
    if not node:
        abort('Failed to create node (name:{0}, image:{1}, size:{2})'.format(name, image, size))

    node = util_wait_till_node_running(name)
    util_print_node(node)
    return node


def aws_destroy_node(name, timeout=30):
    """ Destory a computing node - Ex (cmd:<name>)"""

    node = aws_get_node(name)
    if not node:
        abort('Node does not exist or terminiated ({0})'.format(name))

    if node.destroy():
        node = util_wait_till_node_destroyed(name, timeout)
        if node:
            print >> sys.stderr, 'Node is destroyed ({0})'.format(name)
        else:
            print >> sys.stderr, 'Node is bein destroyed ({0})'.format(name)
    else:
        abort('Failed to destroy node ({0})'.format(name))


def aws_create_volume(name, size, location, snapshot=None):
    """ Create a volume of a given size in a given zone - Ex: (cmd:<name>,<size>,[location],[snapshot])"""
    
    conn = util_get_connection()
    loc = aws_get_location(location)
    if not loc:
        abort('Location does not exist ({0})'.format(location))
    
    volume = conn.create_volume(name=name, size=size, location=loc, snapshot=snapshot)
    return volume


def aws_list_volumes():
    from boto.ec2.connection import EC2Connection
    from boto.utils import get_instance_metadata
    try:
        c = CloudyConfig()
        ACCESS_ID = c.cfg_grid['AWS']['access_id'].strip()
        SECRET_KEY = c.cfg_grid['AWS']['secret_key'].strip()
    except:
        abort('Unable to read ACCESS_ID, SECRET_KEY')

    conn = EC2Connection(ACCESS_ID, SECRET_KEY)
    volumes = [v for v in conn.get_all_volumes()]
    print volumes
    

    