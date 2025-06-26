import os

from fabric import task

from cloudy.sys.core import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_redis_install(c: Context) -> None:
    """Install redis-server and restart the service."""
    c.sudo("apt -y install redis-server")
    sys_etc_git_commit(c, "Installed redis-server")
    sys_restart_service(c, "redis-server")


@task
@Context.wrap_context
def sys_redis_configure_memory(c: Context, memory: int = 0, divider: int = 8) -> None:
    """
    Configure redis-server memory.
    If memory is 0, use total system memory divided by 'divider'.
    """
    redis_conf = "/etc/redis/redis.conf"
    if not memory:
        result = c.run("free -m | awk '/^Mem:/{print $2}'", hide=True)
        total_mem = int(result.stdout.strip())
        memory = total_mem // divider
    memory_bytes = memory * 1024 * 1024
    c.sudo(f'sed -i "s/^maxmemory .*/maxmemory {memory_bytes}/" {redis_conf}')
    sys_etc_git_commit(c, f"Configured redis-server (memory={memory_bytes})")
    sys_restart_service(c, "redis-server")


@task
@Context.wrap_context
def sys_redis_configure_port(c: Context, port: str = "6379") -> None:
    """Configure redis-server port."""
    redis_conf = "/etc/redis/redis.conf"
    c.sudo(f'sed -i "s/^port .*/port {port}/" {redis_conf}')
    sys_etc_git_commit(c, f"Configured redis-server (port={port})")
    sys_restart_service(c, "redis-server")


@task
@Context.wrap_context
def sys_redis_configure_interface(c: Context, interface: str = "0.0.0.0") -> None:
    """Configure redis-server bind interface."""
    redis_conf = "/etc/redis/redis.conf"
    c.sudo(f'sed -i "s/^bind .*/bind {interface}/" {redis_conf}')
    sys_etc_git_commit(c, f"Configured redis-server (interface={interface})")
    sys_restart_service(c, "redis-server")


@task
@Context.wrap_context
def sys_redis_configure_db_file(
    c: Context, path: str = "/var/lib/redis", dump: str = "dump.rdb"
) -> None:
    """Configure redis-server dump file and directory."""
    redis_conf = "/etc/redis/redis.conf"
    c.sudo(f"sed -i '/^dir /d' {redis_conf}")
    c.sudo(f"sh -c 'echo \"dir {path}\" >> {redis_conf}'")
    c.sudo(f"sed -i '/^dbfilename /d' {redis_conf}")
    c.sudo(f"sh -c 'echo \"dbfilename {dump}\" >> {redis_conf}'")
    sys_etc_git_commit(c, f"Configured redis-server (dir={path}, dumpfile={dump})")
    sys_restart_service(c, "redis-server")


@task
@Context.wrap_context
def sys_redis_configure_pass(c: Context, password: str = "") -> None:
    """Set or remove redis-server password."""
    redis_conf = "/etc/redis/redis.conf"
    c.sudo(f"sed -i '/^requirepass /d' {redis_conf}")
    if password:
        c.sudo(f"sh -c 'echo \"requirepass {password}\" >> {redis_conf}'")
    sys_etc_git_commit(
        c,
        (
            "Configured redis-server (password set)"
            if password
            else "Configured redis-server (password removed)"
        ),
    )
    sys_restart_service(c, "redis-server")


@task
@Context.wrap_context
def sys_redis_config(c: Context) -> None:
    """Replace redis.conf with local config and reconfigure memory."""
    cfgdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cfg/redis/redis.conf"))
    remotecfg = "/etc/redis/redis.conf"
    if os.path.exists(cfgdir):
        c.sudo(f"rm -f {remotecfg}")
        c.put(cfgdir, "/tmp/redis.conf")
        c.sudo(f"mv /tmp/redis.conf {remotecfg}")
        sys_redis_configure_memory(c)
        sys_etc_git_commit(c, "Configured redis-server")
        sys_restart_service(c, "redis-server")
    else:
        print(f"Local redis config not found: {cfgdir}")
