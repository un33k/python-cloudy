import os
import re
import sys

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

def sys_memcached_install():
    """ Install memcached - Ex: (cmd)"""
    sudo('apt-get -y install memcached')
    sudo('service memcached restart')
    sys_etc_git_commit('Installed memcached')


def sys_memcached_configure_memory(memory=''):
    """ Configure memcached - Ex: (cmd:[RAM-MB]) """
    memcached_conf = '/etc/memcached.conf'
    if not memory:
        total_mem = sudo("free -m | head -2 | grep Mem | awk '{print $2}'")
        memory = eval(total_mem) / 8    
    sudo('sed -i "s/-m\s\+[0-9]\+/-m {0}/g" {1}'.format(memory, memcached_conf))
    sudo('service memcached restart')
    sys_etc_git_commit('Configured memcached (memory={0})'.format(memory))

def sys_memcached_configure_port(port=11211):
    """ Configure memcached - Ex: (cmd:[port]) """
    memcached_conf = '/etc/memcached.conf'
    sudo('sed -i "s/-p\s\+[0-9]\+/-p {0}/g" {1}'.format(port, memcached_conf))
    sudo('service memcached restart')
    sys_etc_git_commit('Configured memcached (port={0})'.format(port))

def sys_memcached_configure_interface(interface='0.0.0.0'):
    """ Configure memcached - Ex: (cmd:[interface]) """
    memcached_conf = '/etc/memcached.conf'
    sudo('sed -i "s/-l\s\+[0-9.]\+/-l {0}/g" {1}'.format(interface, memcached_conf))
    sudo('service memcached restart')
    sys_etc_git_commit('Configured memcached (interface={0})'.format(interface))

def sys_memcached_config():
    """ Install memcached - Ex: (cmd:)"""
    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'memcached/memcached.conf'))
    remotecfg = '/etc/memcached.conf'
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    sys_memcached_configure_memory()
    sudo('service memcached start')
    sys_etc_git_commit('Configured memcached')




