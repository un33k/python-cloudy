import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo, cd
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit


def web_geoip_install_requirements():
    """Install GeoIP build requirements."""
    requirements = [
        'zlibc',
        'zlib1g-dev',
        'libssl-dev',
        'build-essential',
        'libtool',
    ]
    sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit('Installed GeoIP requirements')

def web_geoip_install_maxmind_api():
    """Install Maxmind C API."""
    tmp_dir = '/tmp/maxmind'
    geoip_url = 'http://www.maxmind.com/download/geoip/api/c/GeoIP.tar.gz'
    sudo(f'rm -rf {tmp_dir}; mkdir -p {tmp_dir}')
    with cd(tmp_dir):
        sudo(f'wget {geoip_url}')
        sudo('tar xvf GeoIP.tar.gz')
        with cd('GeoIP-*'):
            sudo('./configure')
            sudo('make')
            sudo('make install')
    sys_etc_git_commit('Installed Maxmind C API')

def web_geoip_install_maxmind_country(dest_dir='/srv/www/shared/geoip'):
    """Install Maxmind Country Lite database."""
    tmp_dir = '/tmp/maxmind'
    geo_country_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz'
    sudo(f'mkdir -p {tmp_dir}')
    with cd(tmp_dir):
        sudo(f'wget -N -q {geo_country_url}')
        sudo('gunzip -c GeoIP.dat.gz > GeoIP.dat')
        sudo(f'mkdir -p {dest_dir}')
        sudo(f'chown -R :www-data {dest_dir}')
        sudo(f'mv -f *.dat {dest_dir}')
        sudo(f'chmod -R g+wrx {dest_dir}')

def web_geoip_install_maxmind_city(dest_dir='/srv/www/shared/geoip'):
    """Install Maxmind City Lite database."""
    tmp_dir = '/tmp/maxmind'
    geo_city_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
    sudo(f'mkdir -p {tmp_dir}')
    with cd(tmp_dir):
        sudo(f'wget -N -q {geo_city_url}')
        sudo('gunzip -c GeoLiteCity.dat.gz > GeoLiteCity.dat')
        sudo(f'mkdir -p {dest_dir}')
        sudo(f'chown -R :www-data {dest_dir}')
        sudo(f'mv -f *.dat {dest_dir}')
        sudo(f'chmod -R g+wrx {dest_dir}')



