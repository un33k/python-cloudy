"""Recipe for Django web server deployment with database integration."""

from fabric import task

from cloudy.db import pgis, pgpool, psql
from cloudy.srv import recipe_generic_server
from cloudy.sys import core, firewall, python
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context
from cloudy.web import apache, geoip, supervisor, www


@task
@Context.wrap_context
def setup_web(c: Context, cfg_paths=None, generic=True):
    """
    Setup Django web server with comprehensive configuration.

    Installs and configures web server (Apache/Gunicorn), Python environment,
    PostgreSQL with PostGIS, PgPool connection pooling, GeoIP databases,
    and sets up web directories for Django applications.

    Args:
        cfg_paths: Comma-separated config file paths
        generic: Whether to run generic server setup first

    Example:
        fab recipe.web-install --cfg-paths="./.cloudy.generic,./.cloudy.web"
    """
    cfg = CloudyConfig(cfg_paths)

    if generic:
        recipe_generic_server.setup_server(c, cfg_paths)

    # hostname, ips
    hostname = cfg.get_variable("common", "hostname")
    if hostname:
        core.sys_hostname_configure(c, hostname)
        core.sys_add_hosts(c, hostname, "127.0.0.1")

    # setup python stuff
    py_version = cfg.get_variable("common", "python-version")
    python.sys_python_install_common(c, py_version)

    # install webserver
    webserver = cfg.get_variable("webserver", "webserver")
    if webserver and webserver.lower() == "apache":
        apache.web_apache2_install(c)
        apache.web_apache2_install_mods(c)
    elif webserver and webserver.lower() == "gunicorn":
        supervisor.web_supervisor_install(c)

    # create web directory
    www.web_create_data_directory(c)

    webserver_port = cfg.get_variable("webserver", "webserver-port")
    if webserver_port:
        firewall.fw_allow_incoming_port(c, webserver_port)

    # hostname, cache server
    cache_host = cfg.get_variable("cacheserver", "cache-host")
    cache_listen_address = cfg.get_variable("cacheserver", "listen-address")
    if cache_host and cache_listen_address:
        core.sys_add_hosts(c, cache_host, cache_listen_address)

    # create db related
    pg_version = cfg.get_variable("dbserver", "pg-version")
    psql.db_psql_install(c, pg_version)
    pgis_version = cfg.get_variable("dbserver", "pgis-version")
    pgis.db_pgis_install(c, pg_version, pgis_version)

    pgpool.db_pgpool2_install(c)
    db_host = cfg.get_variable("dbserver", "db-host")
    if db_host:
        db_port = cfg.get_variable("dbserver", "db-port", "5432")
        pgpool.db_pgpool2_configure(c, dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable("dbserver", "listen-address")
        if db_listen_address:
            core.sys_add_hosts(c, db_host, db_listen_address)

    geo_ip = cfg.get_variable("webserver", "geo-ip")
    if geo_ip:
        geoip.web_geoip_install_requirements(c)
        geoip.web_geoip_install_maxmind_api(c)
        geoip.web_geoip_install_maxmind_country(c)
        geoip.web_geoip_install_maxmind_city(c)

    # Success message
    print("\n🎉 ✅ DJANGO WEB SERVER SETUP COMPLETED SUCCESSFULLY!")
    print("📋 Configuration Summary:")
    print(f"   └── Hostname: {hostname or 'Not configured'}")
    print(f"   └── Python Version: {py_version or 'System default'}")
    print(f"   └── Web Server: {webserver or 'Not specified'}")
    if webserver_port:
        print(f"   └── Web Port: {webserver_port} (firewall allowed)")
    print(f"   └── PostgreSQL: {pg_version} with PostGIS {pgis_version}")
    if cache_host:
        print(f"   └── Cache Server: {cache_host}:{cache_listen_address}")
    if db_host:
        print(f"   └── Database: {db_host}:{db_port} via PgPool")
    if geo_ip:
        print("   └── GeoIP: MaxMind databases installed")
    print("   └── Web Directory: /var/www")
    print("\n🚀 Django web server is ready for application deployment!")
    if generic:
        admin_user = cfg.get_variable("common", "admin-user", "admin")
        ssh_port = cfg.get_variable("common", "ssh-port", "22")
        print(f"   └── Admin SSH: {admin_user}@{hostname or 'server'}:{ssh_port}")
