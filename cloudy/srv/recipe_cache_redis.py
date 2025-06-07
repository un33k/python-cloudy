from fabric import Connection, task
from cloudy.sys import redis
from cloudy.util.conf import CloudyConfig
from cloudy.sys.firewall import fw_allow_incoming_port_proto
from cloudy.srv.recipe_generic_server import srv_setup_generic_server

@task
def srv_setup_cache_redis(c: Connection, generic: bool = True) -> None:
    """
    Setup a cache server - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        srv_setup_generic_server(c)

    redis_address: str = cfg.get_variable('CACHESERVER', 'redis-address', '0.0.0.0')
    redis_port: str = cfg.get_variable('CACHESERVER', 'redis-port', '6379')

    # Install and configure redis
    redis.sys_redis_install(c)
    redis.sys_redis_config(c)
    redis.sys_redis_configure_memory(c, 0, 2)
    redis.sys_redis_configure_interface(c, redis_address)
    redis.sys_redis_configure_port(c, redis_port)

    # Allow incoming requests
    fw_allow_incoming_port_proto(c, redis_port, 'tcp')
