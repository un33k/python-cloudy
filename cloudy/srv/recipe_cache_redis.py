from fabric import task
from cloudy.util.context import Context
from cloudy.sys import redis
from cloudy.util.conf import CloudyConfig
from cloudy.sys import firewall
from cloudy.srv import recipe_generic_server

@task
@Context.wrap_context
def setup_redis(c: Context, generic: bool = True) -> None:
    """
    Setup a cache server - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        c = recipe_generic_server.setup_server(c)

    redis_address: str = cfg.get_variable('CACHESERVER', 'redis-address', '0.0.0.0')
    redis_port: str = cfg.get_variable('CACHESERVER', 'redis-port', '6379')

    # Install and configure redis
    redis.sys_redis_install(c)
    redis.sys_redis_config(c)
    redis.sys_redis_configure_memory(c, 0, 2)
    redis.sys_redis_configure_interface(c, redis_address)
    redis.sys_redis_configure_port(c, redis_port)

    # Allow incoming requests
    firewall.fw_allow_incoming_port_proto(c, redis_port, 'tcp')
