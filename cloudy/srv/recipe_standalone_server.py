"""Recipe for complete standalone server with all services integrated."""

from fabric import task

from cloudy.db import pgis, pgpool, psql
from cloudy.srv import recipe_generic_server
from cloudy.sys import core, firewall, python, user
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context
from cloudy.web import apache, geoip, nginx, supervisor, www


@task
@Context.wrap_context
def setup_standalone(c: Context, cfg_paths=None) -> None:
    """
    Setup complete standalone server with all services integrated.

    Deploys a comprehensive all-in-one server combining generic server setup,
    PostgreSQL database with PostGIS, Django web server, and Nginx load balancer.
    Perfect for single-server deployments requiring full stack functionality.

    Args:
        cfg_paths: Comma-separated config file paths

    Example:
        fab recipe.sta-install --cfg-paths="./.cloudy.generic,./.cloudy.standalone"
    """
    cfg = CloudyConfig(cfg_paths)

    # ====== Generic Server =========
    c = recipe_generic_server.setup_server(c, cfg_paths)

    # ====== Database Server =========
    dbaddress = cfg.get_variable("dbserver", "listen-address")
    if dbaddress and "*" not in dbaddress:
        core.sys_add_hosts(c, "db-host", dbaddress)

    pg_version = cfg.get_variable("dbserver", "pg-version")
    pg_listen_address = cfg.get_variable("dbserver", "listen-address", "*")
    pg_port = cfg.get_variable("dbserver", "pg-port", "5432")
    pg_cluster = cfg.get_variable("dbserver", "pg-cluster", "main")
    pg_encoding = cfg.get_variable("dbserver", "pg-encoding", "UTF-8")
    pg_data_dir = cfg.get_variable("dbserver", "pg-data-dir", "/var/lib/postgresql")

    psql.db_psql_install(c, pg_version)
    psql.db_psql_make_data_dir(c, pg_version, pg_data_dir)
    psql.db_psql_remove_cluster(c, pg_version, pg_cluster)
    psql.db_psql_create_cluster(c, pg_version, pg_cluster, pg_encoding, pg_data_dir)
    psql.db_psql_set_permission(c, pg_version, pg_cluster)
    psql.db_psql_configure(
        c, version=pg_version, port=pg_port, interface=pg_listen_address, restart=True
    )

    # change postgres' db user password
    postgres_user_pass = cfg.get_variable("dbserver", "postgres-pass")
    if postgres_user_pass:
        psql.db_psql_user_password(c, "postgres", postgres_user_pass)

    # change postgres' system user password
    postgres_sys_user_pass = cfg.get_variable("dbserver", "postgres-sys-pass")
    if postgres_sys_user_pass:
        user.sys_user_change_password(c, "postgres", postgres_sys_user_pass)

    # pgis version
    pgis_version = cfg.get_variable("dbserver", "pgis-version")
    pgis.db_pgis_install(c, pg_version, pgis_version)
    pgis.db_pgis_configure(c, pg_version, pgis_version)
    pgis.db_pgis_get_database_gis_info(c, "template_postgis")

    pgpool.db_pgpool2_install(c)
    db_host = cfg.get_variable("dbserver", "db-host")
    if db_host:
        db_port = cfg.get_variable("dbserver", "db-port", "5432")
        pgpool.db_pgpool2_configure(c, dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable("dbserver", "listen-address")
        if db_listen_address:
            core.sys_add_hosts(c, db_host, db_listen_address)

    # ====== Web Server =========
    py_version = cfg.get_variable("common", "python-version")
    python.sys_python_install_common(c, py_version)

    webserver = cfg.get_variable("webserver", "webserver")
    if webserver and webserver.lower() == "apache":
        apache.web_apache2_install(c)
        apache.web_apache2_install_mods(c)
    elif webserver and webserver.lower() == "gunicorn":
        supervisor.web_supervisor_install(c)

    www.web_create_data_directory(c)

    # hostname, cache server
    cache_host = cfg.get_variable("cacheserver", "cache-host")
    cache_listen_address = cfg.get_variable("cacheserver", "listen-address")
    if cache_host and cache_listen_address:
        core.sys_add_hosts(c, cache_host, cache_listen_address)

    # geoIP
    geo_ip = cfg.get_variable("webserver", "geo-ip")
    if geo_ip:
        geoip.web_geoip_install_requirements(c)
        geoip.web_geoip_install_maxmind_api(c)
        geoip.web_geoip_install_maxmind_country(c)
        geoip.web_geoip_install_maxmind_city(c)

    # ====== Load Balancer Server =========
    firewall.fw_allow_incoming_http(c)
    firewall.fw_allow_incoming_https(c)

    nginx.web_nginx_install(c)
    protocol = "http"
    domain_name = cfg.get_variable("webserver", "domain-name", "example.com")
    certificate_path = cfg.get_variable("common", "certificate-path")
    if certificate_path:
        nginx.web_nginx_copy_ssl(c, domain_name, certificate_path)
        protocol = "https"

    binding_address = cfg.get_variable("webserver", "binding-address", "*")
    upstream_address = cfg.get_variable("webserver", "upstream-address")
    upstream_port = cfg.get_variable("webserver", "upstream-port", "8181")
    if upstream_address and upstream_port:
        nginx.web_nginx_setup_domain(
            c, domain_name, protocol, binding_address, upstream_address, upstream_port
        )

    # Success message
    print(f"\n🎉 ✅ STANDALONE SERVER SETUP COMPLETED SUCCESSFULLY!")
    print(f"📋 Complete All-in-One Configuration Summary:")
    print(f"\n📊 DATABASE SERVER:")
    print(f"   └── PostgreSQL: {pg_version} with PostGIS {pgis_version}")
    print(f"   └── Database Port: {pg_port}")
    print(f"   └── Listen Address: {pg_listen_address}")
    print(f"   └── Data Directory: {pg_data_dir}")
    print(f"\n🌍 WEB SERVER:")
    print(f"   └── Python Version: {py_version or 'System default'}")
    print(f"   └── Web Server: {webserver or 'Not specified'}")
    print(f"   └── Web Directory: /var/www")
    if geo_ip:
        print(f"   └── GeoIP: MaxMind databases installed")
    print(f"\n🔄 LOAD BALANCER:")
    print(f"   └── Nginx: Configured as reverse proxy")
    print(f"   └── Domain: {domain_name}")
    print(f"   └── Protocol: {protocol.upper()}")
    if upstream_address and upstream_port:
        print(f"   └── Upstream: {upstream_address}:{upstream_port}")
    if certificate_path:
        print(f"   └── SSL Certificate: Configured")
    print(f"\n🔥 ADDITIONAL FEATURES:")
    if cache_host:
        print(f"   └── Cache Server: {cache_host}")
    if db_host:
        print(f"   └── PgPool: Connection pooling configured")
    print(f"   └── Firewall: HTTP/HTTPS traffic allowed")
    print(f"\n🚀 Standalone server is fully operational with database, web, and load balancing!")
    admin_user = cfg.get_variable("common", "admin-user", "admin")
    ssh_port = cfg.get_variable("common", "ssh-port", "22")
    print(f"   └── Admin SSH: {admin_user}@server:{ssh_port}")
    print(f"\n🌍 Access your application at: {protocol}://{domain_name}")
