import os
import re
import sys
from operator import itemgetter

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files

from cloudy.db.psql import db_psql_default_installed_version
from cloudy.sys.etc import sys_etc_git_commit


def db_pgis_install(psql_version=''):
    """ Install postgis of a given postgres version - Ex: (cmd:[pgversion])"""
    if not psql_version:
        psql_version = db_psql_default_installed_version()
        
    # requirements
    requirements = '%s' % ' '.join([
        'postgresql-{0}-postgis'.format(psql_version),
        'postgis',
        'proj',
        'gdal-bin',
        'binutils',
        'libgeos-c1',
        'libgeos-3.2.2',
        'libgeos-dev',
        'libgdal1-dev',
        'libgeoip-dev',
        'libpq-dev',
        'libxml2',
        'libxml2-dev'
    ])
    
    # install requirements
    sudo('apt-get -y install {0}'.format(requirements))
    sudo('service postgresql start')
    sys_etc_git_commit('Installed postgis for pqsl ({0})'.format(psql_version))


def db_pgis_get_latest_version(pg_version=''):
    """ Returns the path of the installed postgis given a postgres version - Ex: (cmd:[pgversion])"""
    
    if not pg_version:
        pg_version = db_psql_default_installed_version()
    
    latest_pgis_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('ls /usr/share/postgresql/{0}/contrib/'.format(pg_version))

    version_re = re.compile('postgis-([0-9.]*)\s')
    lines = ret.split('\n')
    versions = []
    for line in lines:
        ver = version_re.search(line.lower())
        if ver:
            versions.append(ver.group(1))

    versions.sort(key = itemgetter(2), reverse = False)
    try:
        latest_pgis_version = versions[0]
    except:
        pass

    print >> sys.stderr, 'Latest installed postgis is: [{0}]'.format(latest_pgis_version)
    return latest_pgis_version


def db_pgis_configure(pg_version='', pgis_version=''):
    """ Configure postgis template - Ex: (cmd:[pgversion],[gisversion]) """
    
    if not pg_version:
        pg_version = db_psql_default_installed_version()
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(pg_version)

    sudo('sudo -u postgres psql -d postgres -c \"UPDATE pg_database SET datistemplate=\'false\' WHERE datname=\'template_postgis\';\"')
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d postgres -c \"DROP database template_postgis;\"')

    sudo('sudo -u postgres createdb -E UTF8 template_postgis')
    with settings(warn_only=True):
        sudo('sudo -u postgres createlang -d template_postgis plpgsql')

    sudo('sudo -u postgres psql -d postgres -c \"UPDATE pg_database SET datistemplate=\'true\' WHERE datname=\'template_postgis\';\"')

    postgis_path = '/usr/share/postgresql/{0}/contrib/postgis-{1}'.format(pg_version, pgis_version)
    sudo('sudo -u postgres psql -d template_postgis -f {0}/postgis.sql'.format(postgis_path))
    sudo('sudo -u postgres psql -d template_postgis -f {0}/spatial_ref_sys.sql'.format(postgis_path))

    sudo('sudo -u postgres psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\"')
    sudo('sudo -u postgres psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\"')
    sudo('sudo -u postgres psql -d template_postgis -c \"GRANT ALL ON geography_columns TO PUBLIC;\"')
    sys_etc_git_commit('Configured postgis ({0}) for pqsl ({1})'.format(pg_version, pgis_version))


def db_pgis_get_database_gis_info(dbname):
    """ Returns the postgis verion of a postgis dababase - Ex: (cmd:<dbname>)"""
    return sudo('sudo -u postgres  psql -d {0} -c \"SELECT postgis_full_version();\"'.format(dbname))





