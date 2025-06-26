"""Recipe for Redis cache server deployment."""

from fabric import task

from cloudy.srv import recipe_generic_server
from cloudy.sys import firewall, redis
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context


@task
@Context.wrap_context
def setup_redis(c: Context, cfg_paths=None, generic: bool = True) -> None:
    """
    Setup redis server with comprehensive configuration.

    Installs and configures Redis cache server with memory optimization,
    network binding, custom port configuration, and firewall rules.

    Args:
        cfg_paths: Comma-separated config file paths
        generic: Whether to run generic server setup first

    Example:
        fab recipe.redis-install --cfg-paths="./.cloudy.generic,./.cloudy.redis"
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

    # Success message
    print(f"\n🎉 ✅ REDIS SERVER SETUP COMPLETED SUCCESSFULLY!")
    print(f"📋 Configuration Summary:")
    print(f"   └── Redis Address: {redis_address}")
    print(f"   └── Redis Port: {redis_port}")
    print(f"   └── Firewall: Port {redis_port}/tcp allowed")
    print(f"   └── Memory: Auto-configured (1/2 of system memory)")
    print(f"\n🚀 Redis server is ready for use!")
    if generic:
        print(f"   └── Admin SSH: Port {cfg.get_variable('common', 'ssh-port', '22')}")
        print(f"   └── Admin User: {cfg.get_variable('common', 'admin-user', 'admin')}")
