import os
from fabric import task
from cloudy.util.context import Context
from cloudy.sys.etc import sys_etc_git_commit

@task
@Context.wrap_context
def web_geoip_install_requirements(c: Context):
    """Install GeoIP build requirements."""
    requirements = [
        'zlibc',
        'zlib1g-dev',
        'libssl-dev',
        'build-essential',
        'libtool',
    ]
    c.sudo(f'apt -y install {" ".join(requirements)}')
    sys_etc_git_commit(c, 'Installed GeoIP requirements')

@task
@Context.wrap_context
def web_geoip_install_maxmind_api(c: Context):
    """Install Maxmind C API."""
    tmp_dir = '/tmp/maxmind'
    geoip_url = 'http://www.maxmind.com/download/geoip/api/c/GeoIP.tar.gz'
    c.sudo(f'rm -rf {tmp_dir} && mkdir -p {tmp_dir}')
    with c.cd(tmp_dir):
        c.sudo(f'wget {geoip_url}')
        c.sudo('tar xvf GeoIP.tar.gz')
        # The extracted folder may vary, so use a wildcard.
        with c.cd('GeoIP-*'):
            c.sudo('./configure')
            c.sudo('make')
            c.sudo('make install')
    sys_etc_git_commit(c, 'Installed Maxmind C API')

@task
@Context.wrap_context
def web_geoip_install_maxmind_country(c: Context, dest_dir='/srv/www/shared/geoip'):
    """Install Maxmind Country Lite database."""
    tmp_dir = '/tmp/maxmind'
    geo_country_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz'
    c.sudo(f'mkdir -p {tmp_dir}')
    with c.cd(tmp_dir):
        c.sudo(f'wget -N -q {geo_country_url}')
        c.sudo('gunzip -c GeoIP.dat.gz > GeoIP.dat')
        c.sudo(f'mkdir -p {dest_dir}')
        c.sudo(f'chown -R :www-data {dest_dir}')
        c.sudo(f'mv -f *.dat {dest_dir}')
        c.sudo(f'chmod -R g+wrx {dest_dir}')

@task
@Context.wrap_context
def web_geoip_install_maxmind_city(c: Context, dest_dir='/srv/www/shared/geoip'):
    """Install Maxmind City Lite database."""
    tmp_dir = '/tmp/maxmind'
    geo_city_url = 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
    c.sudo(f'mkdir -p {tmp_dir}')
    with c.cd(tmp_dir):
        c.sudo(f'wget -N -q {geo_city_url}')
        c.sudo('gunzip -c GeoLiteCity.dat.gz > GeoLiteCity.dat')
        c.sudo(f'mkdir -p {dest_dir}')
        c.sudo(f'chown -R :www-data {dest_dir}')
        c.sudo(f'mv -f *.dat {dest_dir}')
        c.sudo(f'chmod -R g+wrx {dest_dir}')
