import logging
import sys as system
from fabric import task
from invoke.collection import Collection
from paramiko.ssh_exception import AuthenticationException, SSHException

from cloudy.sys import (
    core,
    docker,
    etc,
    firewall,
    memcached,
    mount,
    openvpn,
    ports,
    postfix,
    python,
    redis,
    security,
    ssh,
    swap,
    timezone,
    user,
    vim,
)
from cloudy.db import mysql, pgbouncer, pgis, pgpool, psql
from cloudy.web import apache, geoip, nginx, supervisor, www
from cloudy.aws import ec2
from cloudy.srv import (
    recipe_cache_redis,
    recipe_database_psql_gis,
    recipe_generic_server,
    recipe_loadbalancer_nginx,
    recipe_standalone_server,
    recipe_vpn_server,
    recipe_webserver_django,
)

logging.getLogger().setLevel(logging.ERROR)


@task
def help(c):
    """📖 Python Cloudy - Infrastructure automation toolkit

    🚀 RECIPE COMMANDS (High-level server deployment)
    ├── recipe.gen-install    - Complete server setup with users, security, etc.
    ├── recipe.redis-install  - Redis cache server setup
    ├── recipe.psql-install   - PostGIS-enabled database setup
    ├── recipe.web-install    - Django web server setup
    ├── recipe.lb-install     - Nginx load balancer setup
    ├── recipe.vpn-install    - VPN server setup
    └── recipe.sta-install    - Standalone server setup

    🔧 SYSTEM COMMANDS
    ├── sys.init              - Initialize and update system
    ├── sys.hostname          - Set system hostname
    ├── sys.users             - User management (add, delete, password)
    ├── sys.ssh               - SSH configuration and security
    ├── sys.services          - Service management (start, stop, restart)

    🗄️ DATABASE COMMANDS
    ├── db.pg.*               - PostgreSQL (17 commands)
    ├── db.my.*               - MySQL (6 commands)
    ├── db.pgb.*              - PgBouncer (3 commands)
    ├── db.pgp.*              - PgPool (2 commands)
    └── db.gis.*              - PostGIS (3 commands)

    🌐 WEB SERVER COMMANDS
    ├── web.apache.*          - Apache configuration
    ├── web.nginx.*           - Nginx configuration
    ├── web.supervisor.*      - Process management
    └── web.ssl.*             - SSL certificate management

    🔒 SECURITY & FIREWALL
    ├── fw.*                  - Firewall configuration (17 commands)
    ├── security.*            - Security hardening

    ☁️ CLOUD COMMANDS
    └── aws.*                 - EC2 instance management (17 commands)

    📋 EXAMPLES:

    fab recipe.gen-install --cfg-file="./.cloudy.production"
    fab db.pg.create-user --username=myuser --password=mypass
    fab sys.hostname --hostname=myserver.com
    fab fw.allow-http

    Use 'fab -l' to see all available commands.
    """
    print(help.__doc__)


# Create clean command structure
ns = Collection()
ns.add_task(help)

# RECIPE COMMANDS - High-level deployment recipes
recipe = Collection("recipe")
recipe.add_task(recipe_generic_server.setup_server, name="gen-install")
recipe.add_task(recipe_cache_redis.setup_redis, name="redis-install")
recipe.add_task(recipe_database_psql_gis.setup_db, name="psql-install")
recipe.add_task(recipe_webserver_django.setup_web, name="web-install")
recipe.add_task(recipe_loadbalancer_nginx.setup_lb, name="lb-install")
recipe.add_task(recipe_vpn_server.setup_openvpn, name="vpn-install")
recipe.add_task(recipe_standalone_server.setup_standalone, name="sta-install")
ns.add_collection(recipe)

# SYSTEM COMMANDS - All core system functionality
sys = Collection("sys")

# Core system functions
sys.add_task(core.sys_init, name="init")
sys.add_task(core.sys_update, name="update")
sys.add_task(core.sys_upgrade, name="upgrade")
sys.add_task(core.sys_safe_upgrade, name="safe-upgrade")
sys.add_task(core.sys_hostname_configure, name="hostname")
sys.add_task(core.sys_uname, name="uname")
sys.add_task(core.sys_show_process_by_memory_usage, name="memory-usage")
sys.add_task(core.sys_start_service, name="start-service")
sys.add_task(core.sys_stop_service, name="stop-service")
sys.add_task(core.sys_restart_service, name="restart-service")
sys.add_task(core.sys_reload_service, name="reload-service")
sys.add_task(core.sys_git_install, name="install-git")
sys.add_task(core.sys_install_common, name="install-common")
sys.add_task(core.sys_git_configure, name="configure-git")
sys.add_task(core.sys_add_hosts, name="add-hosts")
sys.add_task(core.sys_locale_configure, name="configure-locale")
sys.add_task(core.sys_mkdir, name="mkdir")
sys.add_task(core.sys_shutdown, name="shutdown")

# User management
sys.add_task(user.sys_user_add, name="add-user")
sys.add_task(user.sys_user_delete, name="delete-user")
sys.add_task(user.sys_user_change_password, name="change-password")
sys.add_task(user.sys_user_add_sudoer, name="add-sudoer")
sys.add_task(user.sys_user_add_passwordless_sudoer, name="add-passwordless-sudoer")
sys.add_task(user.sys_user_remove_sudoer, name="remove-sudoer")

# SSH configuration
sys.add_task(ssh.sys_ssh_set_port, name="ssh-port")
sys.add_task(ssh.sys_ssh_disable_root_login, name="ssh-disable-root")
sys.add_task(ssh.sys_ssh_enable_password_authentication, name="ssh-enable-password")
sys.add_task(ssh.sys_ssh_push_public_key, name="ssh-push-key")

# Time and locale
sys.add_task(timezone.sys_configure_timezone, name="timezone")

# Other system utilities
sys.add_task(swap.sys_swap_configure, name="configure-swap")
sys.add_task(python.sys_python_install_common, name="install-python")
sys.add_task(vim.sys_set_default_editor, name="set-editor")
sys.add_task(postfix.sys_install_postfix, name="install-postfix")
sys.add_task(ports.sys_show_next_available_port, name="next-port")

# Git and etc management
sys.add_task(etc.sys_etc_git_init, name="git-init-etc")
sys.add_task(etc.sys_etc_git_commit, name="git-commit-etc")

ns.add_collection(sys)

# DATABASE COMMANDS - All database functionality
db = Collection("db")

# PostgreSQL commands → db.pg.*
pg = Collection("pg")
pg.add_task(psql.db_psql_install, name="install")
pg.add_task(psql.db_psql_client_install, name="client-install")
pg.add_task(psql.db_psql_configure, name="configure")
pg.add_task(psql.db_psql_create_cluster, name="create-cluster")
pg.add_task(psql.db_psql_remove_cluster, name="remove-cluster")
pg.add_task(psql.db_psql_create_user, name="create-user")
pg.add_task(psql.db_psql_delete_user, name="delete-user")
pg.add_task(psql.db_psql_user_password, name="set-user-pass")
pg.add_task(psql.db_psql_create_database, name="create-db")
pg.add_task(psql.db_psql_delete_database, name="delete-db")
pg.add_task(psql.db_psql_list_users, name="list-users")
pg.add_task(psql.db_psql_list_databases, name="list-dbs")
pg.add_task(psql.db_psql_dump_database, name="dump")
pg.add_task(psql.db_psql_grant_database_privileges, name="grant-privs")
pg.add_task(psql.db_psql_create_gis_database, name="create-gis-db")
pg.add_task(psql.db_psql_latest_version, name="latest-version")
pg.add_task(psql.db_psql_default_installed_version, name="installed-version")
db.add_collection(pg)

# MySQL commands → db.my.*
my = Collection("my")
my.add_task(mysql.db_mysql_server_install, name="install")
my.add_task(mysql.db_mysql_client_install, name="client-install")
my.add_task(mysql.db_mysql_set_root_password, name="set-root-pass")
my.add_task(mysql.db_mysql_create_database, name="create-db")
my.add_task(mysql.db_mysql_create_user, name="create-user")
my.add_task(mysql.db_mysql_grant_user, name="grant-user")
my.add_task(mysql.db_mysql_latest_version, name="latest-version")
db.add_collection(my)

# PgBouncer commands → db.pgb.*
pgb = Collection("pgb")
pgb.add_task(pgbouncer.db_pgbouncer_install, name="install")
pgb.add_task(pgbouncer.db_pgbouncer_configure, name="configure")
pgb.add_task(pgbouncer.db_pgbouncer_set_user_password, name="set-user-pass")
db.add_collection(pgb)

# PgPool commands → db.pgp.*
pgp = Collection("pgp")
pgp.add_task(pgpool.db_pgpool2_install, name="install")
pgp.add_task(pgpool.db_pgpool2_configure, name="configure")
db.add_collection(pgp)

# PostGIS commands → db.gis.*
gis = Collection("gis")
gis.add_task(pgis.db_pgis_install, name="install")
gis.add_task(pgis.db_pgis_configure, name="configure")
gis.add_task(pgis.db_pgis_get_database_gis_info, name="info")
gis.add_task(pgis.db_pgis_get_latest_version, name="latest-version")
db.add_collection(gis)

ns.add_collection(db)

# WEB SERVER COMMANDS - All web server functionality
web = Collection("web")

# Apache commands → web.apache.*
apache_collection = Collection("apache")
apache_collection.add_task(apache.web_apache2_install, name="install")
apache_collection.add_task(apache.web_apache2_setup_domain, name="configure-domain")
apache_collection.add_task(apache.web_apache2_set_port, name="configure-port")
web.add_collection(apache_collection)

# Nginx commands → web.nginx.*
nginx_collection = Collection("nginx")
nginx_collection.add_task(nginx.web_nginx_install, name="install")
nginx_collection.add_task(nginx.web_nginx_setup_domain, name="setup-domain")
nginx_collection.add_task(nginx.web_nginx_copy_ssl, name="copy-ssl")
web.add_collection(nginx_collection)

# Supervisor commands → web.supervisor.*
supervisor_collection = Collection("supervisor")
supervisor_collection.add_task(supervisor.web_supervisor_install, name="install")
supervisor_collection.add_task(supervisor.web_supervisor_setup_domain, name="setup-domain")
web.add_collection(supervisor_collection)

# WWW/Site commands → web.site.*
site = Collection("site")
site.add_task(www.web_create_data_directory, name="create-data-dir")
site.add_task(www.web_create_shared_directory, name="create-shared-dir")
site.add_task(www.web_create_site_directory, name="create-site-dir")
site.add_task(www.web_create_virtual_env, name="create-venv")
site.add_task(www.web_prepare_site, name="prepare-site")
web.add_collection(site)

# GeoIP commands → web.geoip.*
geoip_collection = Collection("geoip")
geoip_collection.add_task(geoip.web_geoip_install_requirements, name="install-requirements")
geoip_collection.add_task(geoip.web_geoip_install_maxmind_api, name="install-api")
geoip_collection.add_task(geoip.web_geoip_install_maxmind_country, name="install-country")
geoip_collection.add_task(geoip.web_geoip_install_maxmind_city, name="install-city")
web.add_collection(geoip_collection)

ns.add_collection(web)

# FIREWALL COMMANDS - All firewall functionality
fw = Collection("fw")
fw.add_task(firewall.fw_install, name="install")
fw.add_task(firewall.fw_secure_server, name="secure-server")
fw.add_task(firewall.fw_allow_incoming_port, name="allow-port")
fw.add_task(firewall.fw_allow_incoming_http, name="allow-http")
fw.add_task(firewall.fw_allow_incoming_https, name="allow-https")
fw.add_task(firewall.fw_allow_incoming_postgresql, name="allow-postgresql")
fw.add_task(firewall.fw_allow_incoming_port_proto, name="allow-port-proto")
fw.add_task(firewall.fw_allow_incoming_host_port, name="allow-host-port")
fw.add_task(firewall.fw_disable, name="disable")
fw.add_task(firewall.fw_wide_open, name="wide-open")
fw.add_task(firewall.fw_reload_ufw, name="reload")
ns.add_collection(fw)

# SECURITY COMMANDS
security_collection = Collection("security")
security_collection.add_task(security.sys_security_install_common, name="install-common")
ns.add_collection(security_collection)

# SERVICES COMMANDS
services = Collection("services")

# Docker
docker_collection = Collection("docker")
docker_collection.add_task(docker.sys_docker_install, name="install")
docker_collection.add_task(docker.sys_docker_config, name="configure")
docker_collection.add_task(docker.sys_docker_user_group, name="add-user")
services.add_collection(docker_collection)

# Redis/Cache
cache = Collection("cache")
cache.add_task(redis.sys_redis_install, name="install")
cache.add_task(redis.sys_redis_config, name="configure")
cache.add_task(redis.sys_redis_configure_port, name="port")
cache.add_task(redis.sys_redis_configure_pass, name="password")
cache.add_task(redis.sys_redis_configure_memory, name="memory")
cache.add_task(redis.sys_redis_configure_interface, name="interface")
services.add_collection(cache)

# Memcached
memcached_collection = Collection("memcached")
memcached_collection.add_task(memcached.sys_memcached_install, name="install")
memcached_collection.add_task(memcached.sys_memcached_config, name="configure")
memcached_collection.add_task(memcached.sys_memcached_configure_port, name="port")
memcached_collection.add_task(memcached.sys_memcached_configure_memory, name="memory")
memcached_collection.add_task(memcached.sys_memcached_configure_interface, name="interface")
services.add_collection(memcached_collection)

# OpenVPN
vpn = Collection("vpn")
vpn.add_task(openvpn.sys_openvpn_docker_install, name="docker-install")
vpn.add_task(openvpn.sys_openvpn_docker_conf, name="docker-conf")
vpn.add_task(openvpn.sys_openvpn_docker_create_client, name="create-client")
vpn.add_task(openvpn.sys_openvpn_docker_revoke_client, name="revoke-client")
vpn.add_task(openvpn.sys_openvpn_docker_show_client_list, name="list-clients")
services.add_collection(vpn)

ns.add_collection(services)

# MOUNT/STORAGE COMMANDS
storage = Collection("storage")
storage.add_task(mount.sys_mount_device, name="mount-device")
storage.add_task(mount.sys_mount_fstab_add, name="add-to-fstab")
ns.add_collection(storage)

# AWS/CLOUD COMMANDS - All EC2 functionality
aws = Collection("aws")
aws.add_task(ec2.aws_list_nodes, name="list-nodes")
aws.add_task(ec2.aws_get_node, name="get-node")
aws.add_task(ec2.aws_create_node, name="create-node")
aws.add_task(ec2.aws_destroy_node, name="destroy-node")
aws.add_task(ec2.aws_list_sizes, name="list-sizes")
aws.add_task(ec2.aws_get_size, name="get-size")
aws.add_task(ec2.aws_list_images, name="list-images")
aws.add_task(ec2.aws_get_image, name="get-image")
aws.add_task(ec2.aws_list_locations, name="list-locations")
aws.add_task(ec2.aws_get_location, name="get-location")
aws.add_task(ec2.aws_list_security_groups, name="list-security-groups")
aws.add_task(ec2.aws_security_group_found, name="find-security-group")
aws.add_task(ec2.aws_list_keypairs, name="list-keypairs")
aws.add_task(ec2.aws_keypair_found, name="find-keypair")
aws.add_task(ec2.aws_create_volume, name="create-volume")
aws.add_task(ec2.aws_list_volumes, name="list-volumes")
ns.add_collection(aws)


# Global exception handling for authentication issues
def handle_auth_exception():
    """Provide helpful guidance for SSH authentication failures."""
    print("\n❌ SSH Authentication Failed!")
    print("\n🔑 To fix this, you need to set up SSH key authentication:")
    print("   1. Generate SSH key (if you don't have one):")
    print("      ssh-keygen -t rsa -b 4096")
    print("\n   2. Copy your SSH key to the server:")
    print("      ssh-copy-id root@10.10.10.198")
    print("\n   3. Test the connection:")
    print("      ssh root@10.10.10.198")
    print("\n   4. Then retry your Fabric command")
    print("\n💡 Alternative: Use password auth (if enabled on server):")
    print("   fab -H root@10.10.10.198 --prompt-for-login-password <command>")
    system.exit(1)


# Monkey patch Fabric to catch authentication errors globally
original_open = None


def patched_connection_open(self):
    """Wrapper for Connection.open() to catch auth errors."""
    try:
        return original_open(self)
    except AuthenticationException:
        handle_auth_exception()
    except SSHException as e:
        if "Authentication failed" in str(e):
            handle_auth_exception()
        raise


# Apply the patch
try:
    from fabric.connection import Connection

    if not hasattr(Connection, "_auth_patched"):
        original_open = Connection.open
        Connection.open = patched_connection_open
        Connection._auth_patched = True
except ImportError:
    pass
