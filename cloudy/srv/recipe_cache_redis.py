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

    redis_port = cfg.get_variable('common', 'redis-port', 6379)
    sys_firewall_allow_incoming_port_proto(redis_port, 'tcp')

    # install redis
    sys_redis_install()
    sys_redis_config()
    sys_redis_configure_memory('', 2)
    sys_redis_configure_port(redis_port)
    bind_address = cfg.get_variable('common', 'bind-address', '0.0.0.0')
    sys_redis_configure_interface(bind_address)
