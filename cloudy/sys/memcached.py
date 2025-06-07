import os
from fabric import task
from cloudy.util.context import Context
from cloudy.sys.core import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit

@task
@Context.wrap_context
def sys_memcached_install(c: Context) -> None:
    """Install memcached and restart the service."""
    c.sudo('apt -y install memcached')
    sys_etc_git_commit(c, 'Installed memcached')
    sys_restart_service(c, 'memcached')

@task
@Context.wrap_context
def sys_memcached_libdev_install(c: Context) -> None:
    """Install libmemcached-dev required by pylibmc."""
    c.sudo('apt -y install libmemcached-dev')

@task
@Context.wrap_context
def sys_memcached_configure_memory(c: Context, memory: int = 0, divider: int = 8) -> None:
    """Configure memcached memory. If memory is 0, use total system memory divided by 'divider'."""
    memcached_conf = '/etc/memcached.conf'
    if not memory:
        result = c.run("free -m | awk '/^Mem:/{print $2}'", hide=True)
        total_mem = int(result.stdout.strip())
        memory = total_mem // divider
    c.sudo(f'sed -i "s/-m\\s\\+[0-9]\\+/-m {memory}/g" {memcached_conf}')
    sys_etc_git_commit(c, f'Configured memcached (memory={memory})')
    sys_restart_service(c, 'memcached')

@task
@Context.wrap_context
def sys_memcached_configure_port(c: Context, port: int = 11211) -> None:
    """Configure memcached port."""
    memcached_conf = '/etc/memcached.conf'
    c.sudo(f'sed -i "s/-p\\s\\+[0-9]\\+/-p {port}/g" {memcached_conf}')
    sys_etc_git_commit(c, f'Configured memcached (port={port})')
    sys_restart_service(c, 'memcached')

@task
@Context.wrap_context
def sys_memcached_configure_interface(c: Context, interface: str = '0.0.0.0') -> None:
    """Configure memcached interface."""
    memcached_conf = '/etc/memcached.conf'
    c.sudo(f'sed -i "s/-l\\s\\+[0-9.]\\+/-l {interface}/g" {memcached_conf}')
    sys_etc_git_commit(c, f'Configured memcached (interface={interface})')
    sys_restart_service(c, 'memcached')

@task
@Context.wrap_context
def sys_memcached_config(c: Context) -> None:
    """Replace memcached.conf with local config and reconfigure memory."""
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'memcached/memcached.conf'))
    remotecfg = '/etc/memcached.conf'
    c.sudo(f'rm -rf {remotecfg}')
    c.put(localcfg, remotecfg)
    sys_memcached_configure_memory(c)
    sys_etc_git_commit(c, 'Configured memcached')
    sys_restart_service(c, 'memcached')
