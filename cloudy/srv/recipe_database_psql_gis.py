import os

from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.web import *
from cloudy.util import *

from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_db(cfg_files):
    """
    Setup a database - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig(filenames=cfg_files)

    srv_setup_generic_server(cfg_files)

    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')
        dbaddress = cfg.get_variable('dbserver', 'listen-address')
        if dbaddress and '*' not in dbaddress:
            sys_add_hosts(hostname, dbaddress)

    ssh_port = cfg.get_variable('common', 'ssh-port', 22)
    sys_firewall_install()
    sys_firewall_secure_server(ssh_port)

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
    pgis_version = cfg.get_variable('dbserver', 'pgis-version', 'latest')
    db_pgis_install(pg_version, pgis_version)
    db_pgis_configure(pg_version, pgis_version)
    db_pgis_get_database_gis_info('template_postgis')
