from cloudy.db import *
from cloudy.sys import *
from cloudy.util import *
from fabric.api import env
from cloudy.srv.generic import setup_generic_server

def srv_setup_psql_database_server(cfg_files='~/.cloudy'):
    """ Setup a postgresql / postgis database server - Ex: (cmd:[cfg-file])"""

    cfg = CloudyConfig(filenames=cfg_files)
    setup_generic_server()

    # hostname, ips
    hostname = cfg.get_variable('dbserver', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')

    # posgresql: version, cluster, data_dir
    pg_version = cfg.get_variable('dbserver', 'pg-version')
    pg_listen_address = cfg.get_variable('dbserver', 'listen-address', '*')
    pg_cluster = cfg.get_variable('dbserver', 'pg-cluster', 'main')
    pg_encoding = cfg.get_variable('dbserver', 'pg-encoding', 'UTF-8')
    pg_data_dir = cfg.get_variable('dbserver', 'pg-data-dir', '/var/lib/postgresql')

    db_psql_install(pg_version)
    db_psql_make_data_dir(pg_version, pg_data_dir)
    db_psql_remove_cluster(pg_version, pg_cluster)
    db_psql_create_cluster(pg_version, pg_cluster, pg_encoding, pg_data_dir)
    db_psql_set_permission(pg_version, pg_cluster)
    db_psql_configure(version=pg_version, port=6432, interface=pg_listen_address, restart=True)
    
    # change postgres' user password
    postgres_user_pass = cfg.get_variable('dbserver', 'postgres-pass')
    if postgres_user_pass:
        db_psql_postgres_password(postgres_user_pass)

    # pgis version
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    if pgis_version:
        db_pgis_install(pg_version)
        db_pgis_configure(pg_version, pgis_version)
        db_pgis_get_database_gis_info('template_postgis')





