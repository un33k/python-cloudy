import sys
import time

from fabric import task
from cloudy.util.context import Context
from cloudy.util.conf import CloudyConfig
from libcloud.compute.types import Provider, NodeState
from libcloud.compute.providers import get_driver
from libcloud.compute.base import Node

def util_print_node(node: Node | None) -> None:
    if node:
        print(', '.join([
            'name: ' + node.name,
            'status: ' + util_get_state2string(node.state),
            'image: '  + node.extra.get('imageId', ''),
            'zone: ' + node.extra.get('availability', ''),
            'key: '  + node.extra.get('keyname', ''),
            'size: ' + node.extra.get('instancetype', ''),
            'pub ip: ' + str(node.public_ips)
        ]), file=sys.stderr)

def util_get_state2string(state: NodeState) -> str:
    compute_state_map = {
        NodeState.RUNNING: 'running',
        NodeState.REBOOTING: 'rebooting',
        NodeState.TERMINATED: 'terminated',
        NodeState.PENDING: 'pending',
        NodeState.UNKNOWN: 'unknown',
    }
    return compute_state_map.get(state, 'unknown')

def util_get_connection(c: Context):
    try:
        cfg = CloudyConfig()
        ACCESS_ID = (cfg.cfg_grid['AWS']['access_id'] or '').strip()
        SECRET_KEY = (cfg.cfg_grid['AWS']['secret_key'] or '').strip()
    except Exception:
        c.abort('Unable to read ACCESS_ID, SECRET_KEY')

    Driver = get_driver(Provider.EC2)
    conn = Driver(ACCESS_ID, SECRET_KEY)
    return conn

def util_wait_till_node(c: Context, name: str, state: NodeState, timeout: int = 10) -> Node | None:
    node = None
    elapsed = 0
    frequency = 5
    while elapsed < timeout:
        node = aws_get_node(c, name)
        if node and node.state == state:
            break
        time.sleep(frequency)
        elapsed += frequency
    return node

def util_wait_till_node_destroyed(c: Context, name: str, timeout: int = 15) -> Node | None:
    return util_wait_till_node(c, name, NodeState.TERMINATED, timeout)

def util_wait_till_node_running(c: Context, name: str, timeout: int = 15) -> Node | None:
    return util_wait_till_node(c, name, NodeState.RUNNING, timeout)

@task
@Context.wrap_context
def util_list_instances(c: Context):
    conn = util_get_connection(c)
    nodes = conn.list_nodes()
    print(nodes, file=sys.stderr)
    return nodes

@task
@Context.wrap_context
def aws_list_sizes(c: Context):
    """ List node sizes - Ex: (cmd)"""
    conn = util_get_connection(c)
    sizes = sorted([i for i in conn.list_sizes()], key=lambda x: x.ram)
    for i in sizes:
        print(' - '.join([i.id, str(i.ram), str(i.price)]), file=sys.stderr)

@task
@Context.wrap_context
def aws_get_size(c: Context, size: str) -> object | None:
    """ Get Node Size - Ex: (cmd:<size>)"""
    conn = util_get_connection(c)
    sizes = [i for i in conn.list_sizes()]
    if size:
        for i in sizes:
            if str(i.ram) == size or i.id == size:
                print(' - '.join([i.id, str(i.ram), str(i.price)]), file=sys.stderr)
                return i
    return None

@task
@Context.wrap_context
def aws_list_images(c: Context):
    """ List available images - Ex: (cmd)"""
    conn = util_get_connection(c)
    images = sorted([i for i in conn.list_images()], key=lambda x: x.id)
    for i in images:
        print(' - '.join([i.id, i.name]), file=sys.stderr)

@task
@Context.wrap_context
def aws_get_image(c: Context, name: str) -> object | None:
    """ Confirm if a node exists - Ex: (cmd:<image>)"""
    conn = util_get_connection(c)
    images = [i for i in conn.list_images()]
    if name:
        for i in images:
            if name == i.id:
                print(' - '.join([i.id, i.name]), file=sys.stderr)
                return i
    return None

@task
@Context.wrap_context
def aws_list_locations(c: Context):
    """ List available locations - Ex: (cmd) """
    conn = util_get_connection(c)
    locations = sorted([i for i in conn.list_locations()], key=lambda x: x.id)
    for i in locations:
        print(' - '.join([getattr(i, "availability_zone", type('', (), {"name": ""})()).name, i.id, i.name, i.country]), file=sys.stderr)

@task
@Context.wrap_context
def aws_get_location(c: Context, name: str) -> object | None:
    """ Confirm if a location exists - Ex: (cmd:<location>)"""
    conn = util_get_connection(c)
    locations = sorted([i for i in conn.list_locations()], key=lambda x: x.id)
    if name:
        for i in locations:
            if getattr(i, "availability_zone", type('', (), {"name": ""})()).name == name:
                print(' - '.join([getattr(i, "availability_zone", type('', (), {"name": ""})()).name, i.id, i.name, i.country]), file=sys.stderr)
                return i
    return None

@task
@Context.wrap_context
def aws_list_security_groups(c: Context):
    """ List available security groups - Ex: (cmd)"""
    conn = util_get_connection(c)
    groups = sorted([i for i in conn.ex_list_security_groups()])
    for i in groups:
        print(i, file=sys.stderr)

@task
@Context.wrap_context
def aws_security_group_found(c: Context, name: str) -> bool:
    """ Confirm if a security group exists - Ex: (cmd:<name>) """
    conn = util_get_connection(c)
    groups = sorted([i for i in conn.ex_list_security_groups()])
    if name:
        for i in groups:
            if i == name:
                print(i, file=sys.stderr)
                return True
    return False

@task
@Context.wrap_context
def aws_list_keypairs(c: Context):
    """ List all available keypairs - Ex: (cmd)"""
    conn = util_get_connection(c)
    nodes = sorted([i for i in conn.ex_describe_all_keypairs()])
    for i in nodes:
        print(i, file=sys.stderr)

@task
@Context.wrap_context
def aws_keypair_found(c: Context, name: str) -> bool:
    """ Confirm if a keypair exists - Ex: (cmd:<name>) """
    conn = util_get_connection(c)
    keys = sorted([i for i in conn.ex_describe_all_keypairs()])
    for i in keys:
        if i == name:
            print(i, file=sys.stderr)
            return True
    return False

@task
@Context.wrap_context
def aws_list_nodes(c: Context):
    """ List all available computing nodes - Ex: (cmd)"""
    conn = util_get_connection(c)
    nodes = sorted([i for i in conn.list_nodes()], key=lambda x: x.name)
    for i in nodes:
        util_print_node(i)

@task
@Context.wrap_context
def aws_get_node(c: Context, name: str) -> Node | None:
    """ Confirm if a computing node exists - Ex: (cmd:<name>) """
    conn = util_get_connection(c)
    nodes = sorted([i for i in conn.list_nodes()], key=lambda x: x.name)
    for i in nodes:
        if i.name == name:
            util_print_node(i)
            return i
    return None

@task
@Context.wrap_context
def aws_create_node(
    c: Context,
    name: str,
    image: str,
    size: str,
    security: str,
    key: str,
    timeout: int = 30
) -> Node | None:
    """ Create a node - Ex: (cmd:<name>,<image>,<size>,[security],[key],[timeout]) """
    conn = util_get_connection(c)

    if aws_get_node(c, name):
        c.abort(f'Node already exists ({name})')

    size_obj = aws_get_size(c, size)
    if not size_obj:
        c.abort(f'Invalid size ({size})')

    if not aws_security_group_found(c, security):
        c.abort(f'Invalid security group ({security})')

    if not aws_keypair_found(c, key):
        c.abort(f'Invalid key ({key})')

    image_obj = aws_get_image(c, image)
    if not image_obj:
        c.abort(f'Invalid image ({image})')

    node = conn.create_node(name=name, image=image_obj, size=size_obj, ex_securitygroup=security, ex_keyname=key)
    if not node:
        c.abort(f'Failed to create node (name:{name}, image:{image}, size:{size})')

    node = util_wait_till_node_running(c, name)
    util_print_node(node)
    return node

@task
@Context.wrap_context
def aws_destroy_node(c: Context, name: str, timeout: int = 30) -> None:
    """ Destroy a computing node - Ex (cmd:<name>)"""
    node = aws_get_node(c, name)
    if not node:
        c.abort(f'Node does not exist or terminated ({name})')

    if node.destroy():
        node = util_wait_till_node_destroyed(c, name, timeout)
        if node:
            print(f'Node is destroyed ({name})', file=sys.stderr)
        else:
            print(f'Node is being destroyed ({name})', file=sys.stderr)
    else:
        c.abort(f'Failed to destroy node ({name})')

@task
@Context.wrap_context
def aws_create_volume(c: Context, name: str, size: int, location: str, snapshot: str = None) -> object:
    """ Create a volume of a given size in a given zone - Ex: (cmd:<name>,<size>,[location],[snapshot])"""
    conn = util_get_connection(c)
    loc = aws_get_location(c, location)
    if not loc:
        c.abort(f'Location does not exist ({location})')

    volume = conn.create_volume(name=name, size=size, location=loc, snapshot=snapshot)
    return volume

@task
@Context.wrap_context
def aws_list_volumes(c: Context) -> None:
    from boto.ec2.connection import EC2Connection
    from boto.utils import get_instance_metadata
    try:
        cfg = CloudyConfig()
        ACCESS_ID = (cfg.cfg_grid['AWS']['access_id'] or '').strip()
        SECRET_KEY = (cfg.cfg_grid['AWS']['secret_key'] or '').strip()
    except Exception:
        c.abort('Unable to read ACCESS_ID, SECRET_KEY')

    conn = EC2Connection(ACCESS_ID, SECRET_KEY)
    volumes = [v for v in conn.get_all_volumes()]
    print(volumes, file=sys.stderr)



