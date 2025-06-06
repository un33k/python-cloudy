import os
from fabric.api import sudo, put
from cloudy.util.common import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit

def sys_memcached_install() -> None:
    """Install memcached and restart the service."""
    sudo('apt -y install memcached')
    sys_etc_git_commit('Installed memcached')
    sys_restart_service('memcached')

def sys_memcached_libdev_install() -> None:
    """Install libmemcached-dev required by pylibmc."""
    sudo('apt -y install libmemcached-dev')

def sys_memcached_configure_memory(memory: int = 0, divider: int = 8) -> None:
    """Configure memcached memory. If memory is 0, use total system memory divided by 'divider'."""
    memcached_conf = '/etc/memcached.conf'
    if not memory:
        total_mem = int(sudo("free -m | awk '/^Mem:/{print $2}'"))
        memory = total_mem // divider
    sudo(f'sed -i "s/-m\\s\\+[0-9]\\+/-m {memory}/g" {memcached_conf}')
    sys_etc_git_commit(f'Configured memcached (memory={memory})')
    sys_restart_service('memcached')

def sys_memcached_configure_port(port: int = 11211) -> None:
    """Configure memcached port."""
    memcached_conf = '/etc/memcached.conf'
    sudo(f'sed -i "s/-p\\s\\+[0-9]\\+/-p {port}/g" {memcached_conf}')
    sys_etc_git_commit(f'Configured memcached (port={port})')
    sys_restart_service('memcached')

def sys_memcached_configure_interface(interface: str = '0.0.0.0') -> None:
    """Configure memcached interface."""
    memcached_conf = '/etc/memcached.conf'
    sudo(f'sed -i "s/-l\\s\\+[0-9.]\\+/-l {interface}/g" {memcached_conf}')
    sys_etc_git_commit(f'Configured memcached (interface={interface})')
    sys_restart_service('memcached')

def sys_memcached_config() -> None:
    """Replace memcached.conf with local config and reconfigure memory."""
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'memcached/memcached.conf'))
    remotecfg = '/etc/memcached.conf'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    sys_memcached_configure_memory()
    sys_etc_git_commit('Configured memcached')
    sys_restart_service('memcached')
