from fabric import task
from cloudy.util.context import Context
from cloudy.db import psql
from cloudy.db import pgis
from cloudy.sys import core
from cloudy.sys import firewall
from cloudy.sys import user
from cloudy.util.conf import CloudyConfig
from cloudy.srv import recipe_generic_server

@task
@Context.wrap_context
def setup_db(c: Context, generic=True):
    """
    Setup a database - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        c = recipe_generic_server.setup_server(c)

    dbaddress = cfg.get_variable('dbserver', 'listen-address')
    if dbaddress and '*' not in dbaddress:
        core.sys_add_hosts(c, 'db-host', dbaddress)

    # postgresql: version, cluster, data_dir
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
    firewall.fw_allow_incoming_port(c, pg_port)

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
