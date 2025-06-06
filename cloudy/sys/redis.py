import os
from fabric.api import sudo, put
from fabric.contrib import files
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_restart_service

def sys_redis_install() -> None:
    """Install redis-server and restart the service."""
    sudo('apt -y install redis-server')
    sys_etc_git_commit('Installed redis-server')
    sys_restart_service('redis-server')

def sys_redis_configure_memory(memory: int = 0, divider: int = 8) -> None:
    """
    Configure redis-server memory.
    If memory is 0, use total system memory divided by 'divider'.
    """
    redis_conf = '/etc/redis/redis.conf'
    if not memory:
        total_mem = int(sudo("free -m | awk '/^Mem:/{print $2}'"))
        memory = total_mem // divider
    memory_bytes = memory * 1024 * 1024
    sudo(f'sed -i "s/^maxmemory .*/maxmemory {memory_bytes}/" {redis_conf}')
    sys_etc_git_commit(f'Configured redis-server (memory={memory_bytes})')
    sys_restart_service('redis-server')

def sys_redis_configure_port(port: int = 6379) -> None:
    """Configure redis-server port."""
    redis_conf = '/etc/redis/redis.conf'
    sudo(f'sed -i "s/^port .*/port {port}/" {redis_conf}')
    sys_etc_git_commit(f'Configured redis-server (port={port})')
    sys_restart_service('redis-server')

def sys_redis_configure_interface(interface: str = '0.0.0.0') -> None:
    """Configure redis-server bind interface."""
    redis_conf = '/etc/redis/redis.conf'
    sudo(f'sed -i "s/^bind .*/bind {interface}/" {redis_conf}')
    sys_etc_git_commit(f'Configured redis-server (interface={interface})')
    sys_restart_service('redis-server')

def sys_redis_configure_db_file(path: str = '/var/lib/redis', dump: str = 'dump.rdb') -> None:
    """Configure redis-server dump file and directory."""
    redis_conf = '/etc/redis/redis.conf'
    sudo(f"sed -i '/^dir /d' {redis_conf}")
    sudo(f'echo "dir {path}" | sudo tee -a {redis_conf}')
    sudo(f"sed -i '/^dbfilename /d' {redis_conf}")
    sudo(f'echo "dbfilename {dump}" | sudo tee -a {redis_conf}')
    sys_etc_git_commit(f'Configured redis-server (dir={path}, dumpfile={dump})')
    sys_restart_service('redis-server')

def sys_redis_configure_pass(password: str = '') -> None:
    """Set or remove redis-server password."""
    redis_conf = '/etc/redis/redis.conf'
    sudo(f"sed -i '/^requirepass /d' {redis_conf}")
    if password:
        sudo(f'echo "requirepass {password}" | sudo tee -a {redis_conf}')
    sys_etc_git_commit('Configured redis-server (password set)' if password else 'Configured redis-server (password removed)')
    sys_restart_service('redis-server')

def sys_redis_config() -> None:
    """Replace redis.conf with local config and reconfigure memory."""
    cfgdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../cfg/redis/redis.conf'))
    remotecfg = '/etc/redis/redis.conf'
    if files.exists(cfgdir):
        sudo(f'rm -f {remotecfg}')
        put(cfgdir, remotecfg, use_sudo=True)
        sys_redis_configure_memory()
        sys_etc_git_commit('Configured redis-server')
        sys_restart_service('redis-server')
    else:
        print(f'Local redis config not found: {cfgdir}')




