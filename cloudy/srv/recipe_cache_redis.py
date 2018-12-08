import os

from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.web import *
from cloudy.util import *

from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_cache_redis(cfg_files, generic=True):
    """
    Setup a cache server - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig(filenames=cfg_files)

    if generic:
        srv_setup_generic_server(cfg_files)

    redis_address = cfg.get_variable('CACHESERVER', 'redis-address', '0.0.0.0')
    redis_port = cfg.get_variable('CACHESERVER', 'redis-port', 6379)

    # install redis
    sys_redis_install()
    sys_redis_config()
    sys_redis_configure_memory('', 2)
    sys_redis_configure_interface(redis_address)
    sys_redis_configure_port(redis_port)

    # allow incoming requests
    sys_firewall_allow_incoming_port_proto(redis_port, 'tcp')
