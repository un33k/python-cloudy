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


def sys_memcached_install():
    """ Install memcached """
    sudo('apt-get -y install memcached')
    sudo('service memcached restart')
    sys_etc_git_commit('Installed memcached')


def sys_memcached_configure(memory=64, port=11211, interface='0.0.0.0'):
    """ Configure memcached. memory (MB), port=11211, interface='0.0.0.0' """
    memcached_conf = '/etc/memcached.conf'
    sudo('sed -i "s/-m\s\+[0-9]\+/-m {0}/g" {1}'.format(memory, memcached_conf))
    sudo('sed -i "s/-p\s\+[0-9]\+/-p {0}/g" {1}'.format(port, memcached_conf))
    sudo('sed -i "s/-l\s\+[0-9.]\+/-l {0}/g" {1}'.format(interface, memcached_conf))
    sys_etc_git_commit('Configured memcached (memory={0}, port={1}, interface={2})'.format(memory, port, interface))




