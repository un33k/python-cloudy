import os
import re
import sys
import time
from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.api import cd
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_mkdir
from cloudy.util.common import sys_restart_service


def sys_redis_install():
    """ Install redis-server - Ex: (cmd)"""
    sudo('apt -y install redis-server')
    sys_etc_git_commit('Installed redis-server')
    sys_restart_service('redis-server')

def sys_redis_configure_memory(memory='', divider=8):
    """ Configure redis-server memory - Ex: (cmd:[RAM-MB]) """
    megs2bytes = lambda m: m * 1024*1024
    redis_conf = '/etc/redis/redis.conf'
    if not memory:
        total_mem = sudo("free -m | head -2 | grep Mem | awk '{print $2}'")
        memory = eval(total_mem) / int(divider)
    memory = megs2bytes(memory)
    sudo('sed -i "s/maxmemory\s\+[0-9]\+/maxmemory {}/g" {}'.format(memory, redis_conf))
    sys_etc_git_commit('Configured redis-server (memory={})'.format(memory))
    sys_restart_service('redis-server')

def sys_redis_configure_port(port=6379):
    """ Configure redis-server port - Ex: (cmd:[port]) """
    redis_conf = '/etc/redis/redis.conf'
    sudo('sed -i "s/port\s\+[0-9]\+/port {}/g" {}'.format(port, redis_conf))
    sys_etc_git_commit('Configured redis-server (port={})'.format(port))
    sys_restart_service('redis-server')

def sys_redis_configure_interface(interface='0.0.0.0'):
    """ Configure redis-server interface - Ex: (cmd:[interface]) """
    redis_conf = '/etc/redis/redis.conf'
    sudo('sed -i "s/bind\s\+[0-9.]\+/bind {}/g" {}'.format(interface, redis_conf))
    sys_etc_git_commit('Configured redis-server (interface={})'.format(interface))
    sys_restart_service('redis-server')

def sys_redis_configure_db_file(path='/var/lib/redis', dump='redis.rdb'):
    """ Configure redis-server dumpfile - Ex: (cmd:[path],[file]) """
    redis_conf = '/etc/redis/redis.conf'
    if path:
        sudo('sed -i /\s*dir\s*.*/d {}'.format(redis_conf))
        sudo('echo "dir {}" >> {}'.format(path, redis_conf))
        # sudo('sed -i \"1idir = \'{}\'\" {}'.format(path, redis_conf))
    if dump:
        sudo('sed -i /\s*dbfilename\s*.*/d {}'.format(redis_conf))
        sudo('echo "dir {}" >> {}'.format(dump, redis_conf))
        # sudo('sed -i \"1idbfilename = \'{}\'\" {}'.format(dump, redis_conf))
    sys_etc_git_commit('Configured redis-server (dir={}, dumpflie={}/)'.format(path, dump))
    sys_restart_service('redis-server')

def sys_redis_configure_pass(password=None):
    """ Configure redis-server set password - Ex: set - (cmd:[password]) - remove (cmd) """
    redis_conf = '/etc/redis/redis.conf'
    sudo('sed -i /\s*\"requirepass"\s*.*/d {}'.format(redis_conf))
    if password:
        sudo('echo "requirepass {}" >> {}'.format(password, redis_conf))
    sys_etc_git_commit('Configured redis-server (passwor={*****})')
    sys_restart_service('redis-server')

def sys_redis_config():
    """ Install redis-server - Ex: (cmd:)"""
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')

    localcfg = os.path.expanduser(os.path.join(cfgdir, 'redis/redis.conf'))
    remotecfg = '/etc/redis/redis.conf'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sys_redis_configure_memory()
    sys_etc_git_commit('Configured redis-server')
    sys_restart_service('redis-server')




