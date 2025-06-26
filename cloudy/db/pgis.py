import re
import sys

from fabric import task

from cloudy.db.psql import db_psql_default_installed_version
from cloudy.sys.core import sys_start_service
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def db_pgis_install(c: Context, psql_version: str = "", pgis_version: str = "") -> None:
    """Install postgis for a given postgres version."""
    if not psql_version:
        psql_version = db_psql_default_installed_version(c)
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(c, psql_version)

    requirements = " ".join(
        [
            f"postgresql-{psql_version}-postgis-{pgis_version}",
            "postgis",
            "libproj-dev",
            "gdal-bin",
            "binutils",
            "libgeos-c1v5",
            "libgeos-dev",
            "libgdal-dev",
            "libgeoip-dev",
            "libpq-dev",
            "libxml2",
            "libxml2-dev",
            "libxml2-utils",
            "libjson-c-dev",
            "xsltproc",
            "docbook-xsl",
            "docbook-mathml",
        ]
    )
    c.sudo("apt -y purge postgis")
    c.sudo(f"apt -y install {requirements}")
    sys_start_service(c, "postgresql")
    sys_etc_git_commit(c, f"Installed postgis for psql ({psql_version})")


@task
@Context.wrap_context
def db_pgis_get_latest_version(c: Context, pg_version: str = "") -> str:
    """Return the latest available postgis version for pg_version."""
    if not pg_version:
        pg_version = db_psql_default_installed_version(c)

    latest_version: str = ""
    result = c.run("apt-cache search --names-only postgis", hide=True, warn=True)
    version_re = re.compile(r"postgresql-[0-9.]+-postgis-([0-9.]+)\s-")
    versions = [
        ver.group(1)
        for line in result.stdout.split("\n")
        if (ver := version_re.search(line.lower()))
    ]
    versions.sort(reverse=True)
    try:
        latest_version = versions[0]
    except IndexError:
        pass

    print(f"Latest available postgis is: [{latest_version}]", file=sys.stderr)
    return latest_version


@task
@Context.wrap_context
def db_pgis_get_latest_libgeos_version(c: Context) -> str:
    """Return the latest libgeos version."""
    latest_version: str = ""
    result = c.run("apt-cache search --names-only libgeos", hide=True, warn=True)

    # Updated regex to match common libgeos package patterns
    version_re = re.compile(r"libgeos-?([0-9]+(?:\.[0-9]+)*)")

    versions = []
    for line in result.stdout.split("\n"):
        if ver := version_re.search(line.lower()):
            versions.append(ver.group(1))

    # Sort versions properly (semantic versioning)
    if versions:
        versions.sort(key=lambda x: [int(i) for i in x.split(".")], reverse=True)
        latest_version = versions[0]

    print(f"Latest available libgeos is: [{latest_version}]", file=sys.stderr)
    return latest_version


@task
@Context.wrap_context
def db_pgis_configure(
    c: Context, pg_version: str = "", pgis_version: str = "", legacy: bool = False
) -> None:
    """Configure postgis template."""
    if not pg_version:
        pg_version = db_psql_default_installed_version(c)
    if not pgis_version:
        pgis_version = db_pgis_get_latest_version(c, pg_version)

    # Allows non-superusers the ability to create from this template
    update_cmd = (
        "sudo -u postgres psql -d postgres -c \"UPDATE pg_database SET datistemplate='false' "
        "WHERE datname='template_postgis';\""
    )
    c.sudo(update_cmd)
    c.sudo(
        'sudo -u postgres psql -d postgres -c "DROP DATABASE template_postgis;"',
        warn=True,
    )

    c.sudo("sudo -u postgres createdb -E UTF8 template_postgis")
    c.sudo(
        'sudo -u postgres psql -d template_postgis -c "CREATE EXTENSION postgis;"',
        warn=True,
    )
    c.sudo(
        'sudo -u postgres psql -d template_postgis -c "CREATE EXTENSION postgis_topology;"',
        warn=True,
    )

    if legacy:
        postgis_path = f"/usr/share/postgresql/{pg_version}/contrib/postgis-{pgis_version}"
        c.sudo(f"sudo -u postgres psql -d template_postgis -f {postgis_path}/legacy.sql")

    # Enabling users to alter spatial tables.
    c.sudo(
        'sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"'
    )
    c.sudo('sudo -u postgres psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"')
    c.sudo(
        'sudo -u postgres psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"'
    )

    sys_etc_git_commit(c, f"Configured postgis ({pgis_version}) for psql ({pg_version})")


@task
@Context.wrap_context
def db_pgis_get_database_gis_info(c: Context, dbname: str) -> None:
    """Return the postgis version of a postgis database."""
    c.sudo(f'sudo -u postgres psql -d {dbname} -c "SELECT PostGIS_Version();"')
