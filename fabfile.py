import logging
from fabric import task
from invoke.collection import Collection

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
    ssh,
    swap,
    timezone,
    user,
    vim,
)
from cloudy.sys import security as security_module
from cloudy.db import mysql, pgbouncer, pgis, pgpool, psql
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

    🚀 SETUP COMMANDS (High-level server deployment)
    ├── setup.server          - Complete server setup with users, security, etc.
    ├── setup.cache           - Redis cache server setup
    ├── setup.database        - PostGIS-enabled database setup
    ├── setup.web             - Django web server setup
    ├── setup.load-balancer   - Nginx load balancer setup
    ├── setup.vpn             - VPN server setup
    └── setup.standalone      - Standalone server setup

    🔧 SYSTEM COMMANDS (Low-level system operations)
    ├── system.hostname       - Set system hostname
    ├── system.users          - User management
    ├── system.ssh            - SSH configuration
    └── system.timezone       - Timezone configuration

    🗄️ DATABASE COMMANDS
    ├── db.psql.install       - Install PostgreSQL
    ├── db.psql.create-user   - Create PostgreSQL user
    ├── db.psql.backup        - Backup PostgreSQL database
    ├── db.mysql.install     - Install MySQL
    └── db.mysql.create-user  - Create MySQL user

    🔒 SECURITY COMMANDS
    ├── security.firewall     - Configure firewall
    └── security.ssh          - Secure SSH access

    📋 EXAMPLES:
    
    fab setup.server --cfg-file="./.cloudy.production"
    fab db.psql.create-user --username=myuser --password=mypass
    fab system.hostname --hostname=myserver.com
    
    Use 'fab -l' to see all available commands.
    """
    print(help.__doc__)


# Create hierarchical command structure with SHORT names
ns = Collection()

# Add main help
ns.add_task(help)

# SETUP COMMANDS - High-level deployment recipes
setup = Collection('setup')
setup.add_task(recipe_generic_server.setup_server, name='server')
setup.add_task(recipe_cache_redis.setup_redis, name='cache')
setup.add_task(recipe_database_psql_gis.setup_db, name='database')
setup.add_task(recipe_webserver_django.setup_web, name='web')
setup.add_task(recipe_loadbalancer_nginx.setup_lb, name='load-balancer')
setup.add_task(recipe_vpn_server.setup_openvpn, name='vpn')
setup.add_task(recipe_standalone_server.setup_standalone, name='standalone')
ns.add_collection(setup)

# SYSTEM COMMANDS - Clean, simple names
system = Collection('system')
system.add_task(core.sys_hostname_configure, name='hostname')
system.add_task(user.sys_user_add, name='add-user')
system.add_task(user.sys_user_change_password, name='change-password')
system.add_task(ssh.sys_ssh_set_port, name='ssh-port')
system.add_task(timezone.sys_configure_timezone, name='timezone')
ns.add_collection(system)

# DATABASE COMMANDS - Organized by database type
db = Collection('db')

# PostgreSQL commands
psql_collection = Collection('psql')
psql_collection.add_task(psql.db_psql_install, name='install')
psql_collection.add_task(psql.db_psql_create_user, name='create-user')
psql_collection.add_task(psql.db_psql_create_database, name='create-database')
psql_collection.add_task(psql.db_psql_dump_database, name='backup')
psql_collection.add_task(psql.db_psql_list_users, name='list-users')
psql_collection.add_task(psql.db_psql_list_databases, name='list-databases')
db.add_collection(psql_collection)

# MySQL commands  
mysql_collection = Collection('mysql')
mysql_collection.add_task(mysql.db_mysql_server_install, name='install')
mysql_collection.add_task(mysql.db_mysql_create_user, name='create-user')
mysql_collection.add_task(mysql.db_mysql_create_database, name='create-database')
mysql_collection.add_task(mysql.db_mysql_set_root_password, name='set-root-password')
db.add_collection(mysql_collection)

ns.add_collection(db)

# SECURITY COMMANDS
security = Collection('security')
security.add_task(firewall.fw_install, name='install-firewall')
security.add_task(firewall.fw_secure_server, name='secure-server')
security.add_task(ssh.sys_ssh_disable_root_login, name='disable-root')
security.add_task(ssh.sys_ssh_enable_password_authentication, name='enable-ssh-password')
ns.add_collection(security)

# WEB COMMANDS
web = Collection('web')
# We'll need to check what web-related tasks are available
ns.add_collection(web)

# CACHE COMMANDS
cache = Collection('cache')
cache.add_task(redis.sys_redis_install, name='install')
cache.add_task(redis.sys_redis_config, name='configure')
cache.add_task(redis.sys_redis_configure_port, name='port')
cache.add_task(redis.sys_redis_configure_pass, name='password')
ns.add_collection(cache)

# DOCKER COMMANDS
docker_collection = Collection('docker')
docker_collection.add_task(docker.sys_docker_install, name='install')
docker_collection.add_task(docker.sys_docker_config, name='configure')
docker_collection.add_task(docker.sys_docker_user_group, name='add-user')
ns.add_collection(docker_collection)