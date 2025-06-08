from fabric import task
from cloudy.util.context import Context
from cloudy.util.conf import CloudyConfig
from cloudy.sys import core
from cloudy.sys import firewall
from cloudy.sys import user
from cloudy.db import psql 
from cloudy.db import pgis 
from cloudy.db import pgpool
from cloudy.web import apache
from cloudy.web import supervisor
from cloudy.web import nginx
from cloudy.web import geoip
from cloudy.web import www
from cloudy.sys import python
from cloudy.srv import recipe_generic_server

@task
@Context.wrap_context
def setup_standalone(c: Context, cfg_file=None) -> None:
    """
    Setup standalone server with config files
    Ex: fab setup-standalone --cfg-file="./.cloudy.generic,./.cloudy.admin"
    """
    if cfg_file:
        # Split comma-separated files and pass as list
        cfg_files = [f.strip() for f in cfg_file.split(',')]
        cfg = CloudyConfig(cfg_files)
    else:
        cfg = CloudyConfig()

    # ====== Generic Server =========
    c = recipe_generic_server.setup_server(c)

    # ====== Database Server =========
    dbaddress = cfg.get_variable('dbserver', 'listen-address')
    if dbaddress and '*' not in dbaddress:
        core.sys_add_hosts(c, 'db-host', dbaddress)

    pg_version = cfg.get_variable('dbserver', 'pg-version')
    pg_listen_address = cfg.get_variable('dbserver', 'listen-address', '*')
    pg_port = cfg.get_variable('dbserver', 'pg-port', '5432')
    pg_cluster = cfg.get_variable('dbserver', 'pg-cluster', 'main')
    pg_encoding = cfg.get_variable('dbserver', 'pg-encoding', 'UTF-8')
    pg_data_dir = cfg.get_variable('dbserver', 'pg-data-dir', '/var/lib/postgresql')

    psql.db_psql_install(c, pg_version)
    psql.db_psql_make_data_dir(c, pg_version, pg_data_dir)
    psql.db_psql_remove_cluster(c, pg_version, pg_cluster)
    psql.db_psql_create_cluster(c, pg_version, pg_cluster, pg_encoding, pg_data_dir)
    psql.db_psql_set_permission(c, pg_version, pg_cluster)
    psql.db_psql_configure(c, version=pg_version, port=pg_port, interface=pg_listen_address, restart=True)

    # change postgres' db user password
    postgres_user_pass = cfg.get_variable('dbserver', 'postgres-pass')
    if postgres_user_pass:
        psql.db_psql_user_password(c, 'postgres', postgres_user_pass)

    # change postgres' system user password
    postgres_sys_user_pass = cfg.get_variable('dbserver', 'postgres-sys-pass')
    if postgres_sys_user_pass:
        user.sys_user_change_password(c, 'postgres', postgres_sys_user_pass)

    # pgis version
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    pgis.db_pgis_install(c, pg_version, pgis_version)
    pgis.db_pgis_configure(c, pg_version, pgis_version)
    pgis.db_pgis_get_database_gis_info(c, 'template_postgis')

    pgpool.db_pgpool2_install(c)
    db_host = cfg.get_variable('dbserver', 'db-host')
    if db_host:
        db_port = cfg.get_variable('dbserver', 'db-port', '5432')
        pgpool.db_pgpool2_configure(c, dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable('dbserver', 'listen-address')
        if db_listen_address:
            core.sys_add_hosts(c, db_host, db_listen_address)

    # ====== Web Server =========
    py_version = cfg.get_variable('common', 'python-version')
    python.sys_python_install_common(c, py_version)

    webserver = cfg.get_variable('webserver', 'webserver')
    if webserver and webserver.lower() == 'apache':
        apache.web_apache2_install(c)
        apache.web_apache2_install_mods(c)
    elif webserver and webserver.lower() == 'gunicorn':
        supervisor.web_supervisor_install(c)

    www.web_create_data_directory(c)

    # hostname, cache server
    cache_host = cfg.get_variable('cacheserver', 'cache-host')
    cache_listen_address = cfg.get_variable('cacheserver', 'listen-address')
    if cache_host and cache_listen_address:
        core.sys_add_hosts(c, cache_host, cache_listen_address)

    # geoIP
    geo_ip = cfg.get_variable('webserver', 'geo-ip')
    if geo_ip:
        geoip.web_geoip_install_requirements(c)
        geoip.web_geoip_install_maxmind_api(c)
        geoip.web_geoip_install_maxmind_country(c)
        geoip.web_geoip_install_maxmind_city(c)

    # ====== Load Balancer Server =========
    firewall.fw_allow_incoming_http(c)
    firewall.fw_allow_incoming_https(c)

    nginx.web_nginx_install(c)
    protocol = 'http'
    domain_name = cfg.get_variable('webserver', 'domain-name', 'example.com')
    certificate_path = cfg.get_variable('common', 'certificate-path')
    if certificate_path:
        nginx.web_nginx_copy_ssl(c, domain_name, certificate_path)
        protocol = 'https'

    binding_address = cfg.get_variable('webserver', 'binding-address', '*')
    upstream_address = cfg.get_variable('webserver', 'upstream-address')
    upstream_port = cfg.get_variable('webserver', 'upstream-port', '8181')
    if upstream_address and upstream_port:
        nginx.web_nginx_setup_domain(c, domain_name, protocol, binding_address, upstream_address, upstream_port)

