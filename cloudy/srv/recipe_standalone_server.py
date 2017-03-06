from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.aws import *
from cloudy.srv import *
from cloudy.web import *
from cloudy.util import *
from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_sta(cfg_files):
    """ Setup a standalone database server - Ex: (cmd:[cfg-file])"""

    cfg = CloudyConfig(filenames=cfg_files)

    # ====== Generic Server =========
    srv_setup_generic_server(cfg_files)

    # ====== Database Server =========
    dbaddress = cfg.get_variable('dbserver', 'listen-address')
    if dbaddress and '*' not in dbaddress:
        sys_add_hosts('db-host', dbaddress)

    # posgresql: version, cluster, data_dir
    pg_version = cfg.get_variable('dbserver', 'pg-version')
    pg_listen_address = cfg.get_variable('dbserver', 'listen-address', '*')
    pg_port = cfg.get_variable('dbserver', 'pg-port', 5432)
    pg_cluster = cfg.get_variable('dbserver', 'pg-cluster', 'main')
    pg_encoding = cfg.get_variable('dbserver', 'pg-encoding', 'UTF-8')
    pg_data_dir = cfg.get_variable('dbserver', 'pg-data-dir', '/var/lib/postgresql')

    db_psql_install(pg_version)
    db_psql_make_data_dir(pg_version, pg_data_dir)
    db_psql_remove_cluster(pg_version, pg_cluster)
    db_psql_create_cluster(pg_version, pg_cluster, pg_encoding, pg_data_dir)
    db_psql_set_permission(pg_version, pg_cluster)
    db_psql_configure(version=pg_version, port=pg_port, interface=pg_listen_address, restart=True)
    sys_firewall_allow_incoming_port(pg_port)

    # change postgres' db user password
    postgres_user_pass = cfg.get_variable('dbserver', 'postgres-pass')
    if postgres_user_pass:
        db_psql_user_password('postgres', postgres_user_pass)

    # change postgres' system user password
    postgres_sys_user_pass = cfg.get_variable('dbserver', 'postgres-sys-pass')
    if postgres_sys_user_pass:
        sys_user_change_password('postgres', postgres_sys_user_pass)

    # pgis version
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    db_pgis_install(pg_version, pgis_version)
    db_pgis_configure(pg_version, pgis_version)
    db_pgis_get_database_gis_info('template_postgis')

    db_pgpool2_install()
    db_host = cfg.get_variable('dbserver', 'db-host')
    if db_host:
        db_port = cfg.get_variable('dbserver', 'db-port', 5432)
        db_pgpool2_configure(dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable('dbserver', 'listen-address')
        if db_listen_address:
            sys_add_hosts(db_host, db_listen_address)


    # ====== Web Server =========
    # setup python stuff
    py_version = cfg.get_variable('common', 'python-version')
    sys_python_install_common(py_version)

    # install webserver
    webserver = cfg.get_variable('webserver', 'webserver')
    if webserver.lower() == 'apache':
        web_apache_install()
        web_apache2_install_mods()
    elif webserver.lower() == 'gunicorn':
        web_supervisor_install()

    # create web directory
    web_create_data_directory()

    webserver_port = cfg.get_variable('webserver', 'webserver-port')
    sys_firewall_allow_incoming_port(webserver_port)

    # hostname, cache server
    cache_host = cfg.get_variable('cacheserver', 'cache-host')
    cache_listen_address = cfg.get_variable('cacheserver', 'listen-address')
    if cache_host and cache_listen_address:
        sys_add_hosts(cache_host, cache_listen_address)

    # geoIP
    web_geoip_install_requirements()
    web_geoip_install_maxmind_api()
    web_geoip_install_maxmind_country()
    web_geoip_install_maxmind_city()
