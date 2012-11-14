
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


def web_geoip_install_requirements():
    """ Install GeoIP Requirements  - Ex: (cmd)"""
    requirements = '%s' % ' '.join([
        'zlibc',
        'zlib1g-dev',
        'libssl-dev',
        'build-essential',
        # 'linux-headers-`uname -r`',
        'libtool',
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    sys_etc_git_commit('Installed GeoIP')

def web_geoip_install_maxmind_api():
    """ Install Maxmind C API - Ex: (cmd) """
    tmp_dir = '/tmp/maxmind'
    geoip_url = 'http://www.maxmind.com/download/geoip/api/c/GeoIP.tar.gz'
    geocity_url = 'http://www.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
    sudo('rm -rf {0}; mkdir -p {0}'.format(tmp_dir))
    with cd(tmp_dir):
        sudo('wget {0}'.format(geoip_url))
        sudo('tar xvf GeoIP.tar.gz')
        with cd('GeoIP-*'):
            sudo('./configure')
            sudo('make')
            sudo('make install')
    sys_etc_git_commit('Installed Maxmind C API')

def web_geoip_install_maxmind_country(dest_dir='/usr/local/share/GeoIP'):
    """ Install Maxmind Country Lite - Ex: (cmd:[dest_dir]) """
    tmp_dir = '/tmp/maxmind'
    geocity_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz'
    sudo('rm -rf {0}; mkdir -p {0}'.format(tmp_dir))
    with cd(tmp_dir):
        sudo('wget {0}'.format(geocity_url))
        sudo('gzip -d GeoIP.dat.gz')
        sudo('mkdir -p {0}'.format(dest_dir))
        sudo('mv -f *.dat {0}'.format(dest_dir))


def web_geoip_install_maxmind_city(dest_dir='/usr/local/share/GeoIP'):
    """ Install Maxmind City Lite - Ex: (cmd:[dest_dir]) """
    tmp_dir = '/tmp/maxmind'
    geocity_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
    sudo('rm -rf {0}; mkdir -p {0}'.format(tmp_dir))
    with cd(tmp_dir):
        sudo('wget {0}'.format(geocity_url))
        sudo('gzip -d GeoLiteCity.dat.gz')
        sudo('mkdir -p {0}'.format(dest_dir))
        sudo('mv -f *.dat {0}'.format(dest_dir))


