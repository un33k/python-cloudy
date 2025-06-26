"""Recipe for PostgreSQL database server with PostGIS spatial extensions."""

from fabric import task

from cloudy.db import pgis, psql
from cloudy.srv import recipe_generic_server
from cloudy.sys import core, firewall, user
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context


@task
@Context.wrap_context
def setup_db(c: Context, cfg_paths=None, generic=True):
    """
    Setup PostgreSQL database server with PostGIS spatial extensions.

    Installs and configures PostgreSQL with PostGIS for spatial database
    operations, including cluster creation, user management, and firewall setup.

    Args:
        cfg_paths: Comma-separated config file paths
        generic: Whether to run generic server setup first

    Example:
        fab recipe.psql-install --cfg-paths="./.cloudy.generic,./.cloudy.db"
    """
    cfg = CloudyConfig(cfg_paths)

    if generic:
        c = recipe_generic_server.setup_server(c, cfg_paths)

    dbaddress = cfg.get_variable("dbserver", "listen-address")
    if dbaddress and "*" not in dbaddress:
        core.sys_add_hosts(c, "db-host", dbaddress)

    # postgresql: version, cluster, data_dir
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
    firewall.fw_allow_incoming_port(c, pg_port)

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

    # Success message
    print("\n🎉 ✅ POSTGRESQL + POSTGIS DATABASE SERVER SETUP COMPLETED!")
    print("📋 Configuration Summary:")
    print(f"   └── PostgreSQL Version: {pg_version}")
    print(f"   └── PostGIS Version: {pgis_version}")
    print(f"   └── Database Port: {pg_port}")
    print(f"   └── Listen Address: {pg_listen_address}")
    print(f"   └── Cluster: {pg_cluster}")
    print(f"   └── Data Directory: {pg_data_dir}")
    print(f"   └── Encoding: {pg_encoding}")
    print(f"   └── Firewall: Port {pg_port} allowed")
    if postgres_user_pass:
        print("   └── Postgres User: Password configured")
    if postgres_sys_user_pass:
        print("   └── System User: Password configured")
    print("\n🚀 PostgreSQL with PostGIS is ready for spatial database operations!")
    if generic:
        admin_user = cfg.get_variable("common", "admin-user", "admin")
        ssh_port = cfg.get_variable("common", "ssh-port", "22")
        print(f"   └── Admin SSH: {admin_user}@server:{ssh_port}")
