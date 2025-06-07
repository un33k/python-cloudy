from fabric import Connection, task
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
    db_pgis_get_database_gis_info
)
from cloudy.sys.core import sys_add_hosts
from cloudy.sys.firewall import fw_allow_incoming_port
from cloudy.sys.user import sys_user_change_password
from cloudy.util.conf import CloudyConfig
from cloudy.srv.recipe_generic_server import srv_setup_generic_server

@task
def srv_setup_db(c: Connection, generic=True):
    """
    Setup a database - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        srv_setup_generic_server(c)

    dbaddress = cfg.get_variable('dbserver', 'listen-address')
    if dbaddress and '*' not in dbaddress:
        sys_add_hosts(c, 'db-host', dbaddress)

    # postgresql: version, cluster, data_dir
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
    fw_allow_incoming_port(c, pg_port)

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
