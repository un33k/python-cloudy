from fabric import task

from cloudy.srv import recipe_generic_server
from cloudy.sys import firewall, redis
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context


@task
@Context.wrap_context
def setup_redis(c: Context, cfg_paths=None, generic: bool = True) -> None:
    """
    Setup redis server with config files
    Ex: fab setup-redis --cfg-paths="./.cloudy.generic,./.cloudy.admin"
    """
    cfg = CloudyConfig(cfg_paths)

    if generic:
        recipe_generic_server.setup_server(c, cfg_paths)

    redis_address: str = cfg.get_variable("CACHESERVER", "redis-address", "0.0.0.0")
    redis_port: str = cfg.get_variable("CACHESERVER", "redis-port", "6379")

    # Install and configure redis
    redis.sys_redis_install(c)
    redis.sys_redis_config(c)
    redis.sys_redis_configure_memory(c, 0, 2)
    redis.sys_redis_configure_interface(c, redis_address)
    redis.sys_redis_configure_port(c, redis_port)

    # Allow incoming requests
    firewall.fw_allow_incoming_port_proto(c, redis_port, "tcp")
