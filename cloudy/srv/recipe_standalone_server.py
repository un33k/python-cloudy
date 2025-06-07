from fabric import Connection, task
from cloudy.util.conf import CloudyConfig
from cloudy.sys.core import sys_add_hosts
from cloudy.sys.firewall import fw_allow_incoming_http, fw_allow_incoming_https
from cloudy.sys.user import sys_user_change_password
from cloudy.db.psql import (
    db_psql_install,
    db_psql_make_data_dir,
    db_psql_remove_cluster,
    db_psql_create_cluster,
    db_psql_set_permission,
    db_psql_configure,
    db_psql_user_password,
)
from cloudy.db.pgis import (
    db_pgis_install,
    db_pgis_configure,
    db_pgis_get_database_gis_info,
)
from cloudy.db.pgpool import db_pgpool2_install, db_pgpool2_configure
from cloudy.web.apache import web_apache2_install_mods, web_apache2_install
from cloudy.web.supervisor import web_supervisor_install
from cloudy.web.nginx import web_nginx_install, web_nginx_copy_ssl, web_nginx_setup_domain
from cloudy.web.geoip import (
    web_geoip_install_requirements,
    web_geoip_install_maxmind_api,
    web_geoip_install_maxmind_country,
    web_geoip_install_maxmind_city,
)
from cloudy.web.www import web_create_data_directory
from cloudy.sys.python import sys_python_install_common
from cloudy.srv.recipe_generic_server import srv_setup_generic_server

@task
def srv_setup_sta(c: Connection) -> None:
    """Setup a standalone database/web/loadbalancer server - Ex: (cmd:[cfg-file])"""
    cfg = CloudyConfig()

    # ====== Generic Server =========
    srv_setup_generic_server(c)

    # ====== Database Server =========
    dbaddress = cfg.get_variable('dbserver', 'listen-address')
    if dbaddress and '*' not in dbaddress:
        sys_add_hosts(c, 'db-host', dbaddress)

    pg_version = cfg.get_variable('dbserver', 'pg-version')
    pg_listen_address = cfg.get_variable('dbserver', 'listen-address', '*')
    pg_port = cfg.get_variable('dbserver', 'pg-port', '5432')
    pg_cluster = cfg.get_variable('dbserver', 'pg-cluster', 'main')
    pg_encoding = cfg.get_variable('dbserver', 'pg-encoding', 'UTF-8')
    pg_data_dir = cfg.get_variable('dbserver', 'pg-data-dir', '/var/lib/postgresql')

    db_psql_install(c, pg_version)
    db_psql_make_data_dir(c, pg_version, pg_data_dir)
    db_psql_remove_cluster(c, pg_version, pg_cluster)
    db_psql_create_cluster(c, pg_version, pg_cluster, pg_encoding, pg_data_dir)
    db_psql_set_permission(c, pg_version, pg_cluster)
    db_psql_configure(c, version=pg_version, port=pg_port, interface=pg_listen_address, restart=True)

    # change postgres' db user password
    postgres_user_pass = cfg.get_variable('dbserver', 'postgres-pass')
    if postgres_user_pass:
        db_psql_user_password(c, 'postgres', postgres_user_pass)

    # change postgres' system user password
    postgres_sys_user_pass = cfg.get_variable('dbserver', 'postgres-sys-pass')
    if postgres_sys_user_pass:
        sys_user_change_password(c, 'postgres', postgres_sys_user_pass)

    # pgis version
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    db_pgis_install(c, pg_version, pgis_version)
    db_pgis_configure(c, pg_version, pgis_version)
    db_pgis_get_database_gis_info(c, 'template_postgis')

    db_pgpool2_install(c)
    db_host = cfg.get_variable('dbserver', 'db-host')
    if db_host:
        db_port = cfg.get_variable('dbserver', 'db-port', '5432')
        db_pgpool2_configure(c, dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable('dbserver', 'listen-address')
        if db_listen_address:
            sys_add_hosts(c, db_host, db_listen_address)

    # ====== Web Server =========
    py_version = cfg.get_variable('common', 'python-version')
    sys_python_install_common(c, py_version)

    webserver = cfg.get_variable('webserver', 'webserver')
    if webserver and webserver.lower() == 'apache':
        web_apache2_install(c)
        web_apache2_install_mods(c)
    elif webserver and webserver.lower() == 'gunicorn':
        web_supervisor_install(c)

    web_create_data_directory(c)

    # hostname, cache server
    cache_host = cfg.get_variable('cacheserver', 'cache-host')
    cache_listen_address = cfg.get_variable('cacheserver', 'listen-address')
    if cache_host and cache_listen_address:
        sys_add_hosts(c, cache_host, cache_listen_address)

    # geoIP
    geo_ip = cfg.get_variable('webserver', 'geo-ip')
    if geo_ip:
        web_geoip_install_requirements(c)
        web_geoip_install_maxmind_api(c)
        web_geoip_install_maxmind_country(c)
        web_geoip_install_maxmind_city(c)

    # ====== Load Balancer Server =========
    fw_allow_incoming_http(c)
    fw_allow_incoming_https(c)

    web_nginx_install(c)
    protocol = 'http'
    domain_name = cfg.get_variable('webserver', 'domain-name', 'example.com')
    certificate_path = cfg.get_variable('common', 'certificate-path')
    if certificate_path:
        web_nginx_copy_ssl(c, domain_name, certificate_path)
        protocol = 'https'

    binding_address = cfg.get_variable('webserver', 'binding-address', '*')
    upstream_address = cfg.get_variable('webserver', 'upstream-address')
    upstream_port = cfg.get_variable('webserver', 'upstream-port', '8181')
    if upstream_address and upstream_port:
        web_nginx_setup_domain(c, domain_name, protocol, binding_address, upstream_address, upstream_port)

