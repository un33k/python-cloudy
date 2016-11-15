import os

from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.web import *
from cloudy.util import *

from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_cache(cfg_files):
    """
    Setup a cache server - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig(filenames=cfg_files)

    srv_setup_generic_server(cfg_files)

    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')

    redis_port = cfg.get_variable('common', 'redis-port', 6379)
    ssh_port = cfg.get_variable('common', 'ssh-port', 22)
    sys_firewall_install()
    sys_firewall_allow_incoming_port_proto(redis_port, 'tcp')
    sys_firewall_secure_server(ssh_port)

    # install redis
    sys_redis_install()
    sys_redis_config()
    sys_redis_configure_memory('', 2)
    sys_redis_configure_port(redis_port)
    bind_address = cfg.get_variable('common', 'bind-address', '0.0.0.0')
    sys_redis_configure_interface(bind_address)
