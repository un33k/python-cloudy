import re
import sys
from operator import itemgetter
from fabric.api import run, sudo, settings, hide
from cloudy.db.psql import db_psql_default_installed_version
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.common import sys_start_service


def db_pgis_install(psql_version='', pgis_version=''):
    """Install postgis for a given postgres version."""
    if not psql_version:
        psql_version = db_psql_default_installed_version()
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(psql_version)
    libgeos_version = db_pgis_get_latest_libgeos_version()
    requirements = ' '.join([
        f'postgresql-{psql_version}-postgis-{pgis_version}',
        'postgis',
        'libproj-dev',
        'gdal-bin',
        'binutils',
        f'libgeos-{libgeos_version}',
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
    sudo('apt -y purge postgis')
    sudo(f'apt -y install {requirements}')
    sys_start_service('postgresql')
    sys_etc_git_commit(f'Installed postgis for psql ({psql_version})')


def db_pgis_get_latest_version(pg_version=''):
    """Return the latest available postgis version for pg_version."""
    if not pg_version:
        pg_version = db_psql_default_installed_version()

    latest_version = ''
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        ret = run('apt-cache search --names-only postgis')

    version_re = re.compile(r'postgresql-[0-9.]+-postgis-([0-9.]+)\s-')
    versions = [ver.group(1) for line in ret.split('\n') if (ver := version_re.search(line.lower()))]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass

    print(f'Latest available postgis is: [{latest_version}]', file=sys.stderr)
    return latest_version


def db_pgis_get_latest_libgeos_version():
    """Return the latest libgeos version."""

    latest_version = ''
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        ret = run('apt-cache search --names-only libgeos')

    version_re = re.compile(r'libgeos-([0-9.]+)\s-')
    versions = [ver.group(1) for line in ret.split('\n') if (ver := version_re.search(line.lower()))]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass

    print(f'Latest available libgeos is: [{latest_version}]', file=sys.stderr)
    return latest_version


def db_pgis_configure(pg_version='', pgis_version='', legacy=False):
    """Configure postgis template."""
    if not pg_version:
        pg_version = db_psql_default_installed_version()
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(pg_version)

    # Allows non-superusers the ability to create from this template
    sudo('sudo -u postgres psql -d postgres -c "UPDATE pg_database SET datistemplate=\'false\' WHERE datname=\'template_postgis\';"')
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d postgres -c "DROP DATABASE template_postgis;"')

    sudo('sudo -u postgres createdb -E UTF8 template_postgis')
    with settings(warn_only=True):
        sudo('sudo -u postgres psql -d template_postgis -c "CREATE EXTENSION postgis;"')
        sudo('sudo -u postgres psql -d template_postgis -c "CREATE EXTENSION postgis_topology;"')

    if legacy:
        postgis_path = f'/usr/share/postgresql/{pg_version}/contrib/postgis-{pgis_version}'
        sudo(f'sudo -u postgres psql -d template_postgis -f {postgis_path}/legacy.sql')

    # Enabling users to alter spatial tables.
    sudo('sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"')
    sudo('sudo -u postgres psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"')
    sudo('sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"')

    sys_etc_git_commit(f'Configured postgis ({pgis_version}) for psql ({pg_version})')


def db_pgis_get_database_gis_info(dbname):
    """Return the postgis version of a postgis database."""
    sudo(f'sudo -u postgres psql -d {dbname} -c "SELECT PostGIS_Version();"')





