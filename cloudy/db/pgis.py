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


def db_pgis_install(psql_version='', pgis_version=''):
    """ Install postgis of a given postgres version - Ex: (cmd:[psql_version],[pgis_version])"""
    if not psql_version:
        psql_version = db_psql_default_installed_version()
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(psql_version)

    libgeos_version = db_pgis_get_latest_libgeos_version()

    # requirements
    requirements = '%s' % ' '.join([
        'postgresql-{}-postgis-{}'.format(psql_version, pgis_version),
        'postgis',
        'libproj-dev',
        'gdal-bin',
        'binutils',
        'libgeos-c1',
        'libgeos-{}'.format(libgeos_version),
        'libgeos-dev',
        'libgdal1-dev',
        'libgdal-dev',
        'libgeoip-dev',
        'libpq-dev',
        'libxml2',
        'libxml2-dev',
        'libxml2-utils',
        'libjson0-dev',
        'xsltproc',
        'docbook-xsl',
        'docbook-mathml',
    ])

    # install requirements
    sudo('apt-get -y purge postgis')
    sudo('apt-get -y install {}'.format(requirements))
    sudo('service postgresql start')
    sys_etc_git_commit('Installed postgis for pqsl ({})'.format(psql_version))


def db_pgis_get_latest_version(pg_version=''):
    """ Returns the latest available postgis version for pg_version - Ex: (cmd:[pg_version])"""

    if not pg_version:
        pg_version = db_psql_default_installed_version()

    latest_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('apt-cache search --names-only postgis')

    version_re = re.compile('postgresql-([0-9.]*)-postgis-([0-9.]*)\s-')
    lines = ret.split('\n')
    versions = []
    for line in lines:
        ver = version_re.search(line.lower())
        if ver:
            versions.append(ver.group(2))

    versions.sort(key = itemgetter(2), reverse = False)
    try:
        latest_version = versions[0]
    except:
        pass

    print >> sys.stderr, 'Latest available postgis is: [{}]'.format(latest_version)
    return latest_version

def db_pgis_get_latest_libgeos_version():
    """ Returns the lastest libgeos version - Ex: (cmd)"""

    latest_version = ''
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('apt-cache search --names-only libgeos')

    version_re = re.compile('libgeos-([0-9.]*)\s-')
    lines = ret.split('\n')
    versions = []
    for line in lines:
        ver = version_re.search(line.lower())
        if ver:
            versions.append(ver.group(1))

    versions.sort(key = itemgetter(2), reverse = True)
    try:
        latest_version = versions[0]
    except:
        pass

    print >> sys.stderr, 'Latest available libgeos is: [{}]'.format(latest_version)
    return latest_version


def db_pgis_configure(pg_version='', pgis_version='', legacy=False):
    """ Configure postgis template - Ex: (cmd:[pgversion],[gisversion]) """

    if not pg_version:
        pg_version = db_psql_default_installed_version()
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(pg_version)

    # Allows non-superusers the ability to create from this template
    sudo('sudo -u postgres psql -d postgres -c \"UPDATE pg_database SET datistemplate=\'false\' WHERE datname=\'template_postgis\';\"')
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d postgres -c \"DROP database template_postgis;\"')

    sudo('sudo -u postgres createdb -E UTF8 template_postgis')
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d template_postgis -c \"CREATE EXTENSION postgis;\"')
        sudo('sudo -u postgres psql -d template_postgis -c \"CREATE EXTENSION postgis_topology;\"')

    if legacy:
        postgis_path = '/usr/share/postgresql/{}/contrib/postgis-{}'.format(pg_version, pgis_version)
        sudo('sudo -u postgres psql -d template_postgis -f {}/legacy.sql'.format(postgis_path))

    # Enabling users to alter spatial tables.
    sudo('sudo -u postgres psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\"')
    sudo('sudo -u postgres psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\"')
    sudo('sudo -u postgres psql -d template_postgis -c \"GRANT ALL ON geography_columns TO PUBLIC;\"')

    sys_etc_git_commit('Configured postgis ({}) for pqsl ({})'.format(pg_version, pgis_version))


def db_pgis_get_database_gis_info(dbname):
    """ Returns the postgis verion of a postgis dababase - Ex: (cmd:<dbname>)"""
    sudo('sudo -u postgres  psql -d {} -c \"SELECT PostGIS_Version();\";'.format(dbname))





