from fabric import task
from cloudy.util.context import Context
from cloudy.sys import core
from cloudy.sys import python
from cloudy.web import apache
from cloudy.web import supervisor
from cloudy.web import geoip
from cloudy.sys import firewall 
from cloudy.db import pgpool
from cloudy.web import www
from cloudy.db import psql
from cloudy.db import pgis
from cloudy.util.conf import CloudyConfig
from cloudy.srv import recipe_generic_server

@task
@Context.wrap_context
def setup_web(c: Context, cfg_file=None, generic=True):
    """
    Setup web server with config files
    Ex: fab setup-web --cfg-file="./.cloudy.generic,./.cloudy.admin"
    """
    if cfg_file:
        # Split comma-separated files and pass as list
        cfg_files = [f.strip() for f in cfg_file.split(',')]
        cfg = CloudyConfig(cfg_files)
    else:
        cfg = CloudyConfig()

    if generic:
        recipe_generic_server.setup_server(c)

    # hostname, ips
    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        core.sys_hostname_configure(c, hostname)
        core.sys_add_hosts(c, hostname, '127.0.0.1')

    # setup python stuff
    py_version = cfg.get_variable('common', 'python-version')
    python.sys_python_install_common(c, py_version)

    # install webserver
    webserver = cfg.get_variable('webserver', 'webserver')
    if webserver and webserver.lower() == 'apache':
        apache.web_apache2_install(c)
        apache.web_apache2_install_mods(c)
    elif webserver and webserver.lower() == 'gunicorn':
        supervisor.web_supervisor_install(c)

    # create web directory
    www.web_create_data_directory(c)

    webserver_port = cfg.get_variable('webserver', 'webserver-port')
    if webserver_port:
        firewall.fw_allow_incoming_port(c, webserver_port)

    # hostname, cache server
    cache_host = cfg.get_variable('cacheserver', 'cache-host')
    cache_listen_address = cfg.get_variable('cacheserver', 'listen-address')
    if cache_host and cache_listen_address:
        core.sys_add_hosts(c, cache_host, cache_listen_address)

    # create db related
    pg_version = cfg.get_variable('dbserver', 'pg-version')
    psql.db_psql_install(c, pg_version)
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    pgis.db_pgis_install(c, pg_version, pgis_version)

    pgpool.db_pgpool2_install(c)
    db_host = cfg.get_variable('dbserver', 'db-host')
    if db_host:
        db_port = cfg.get_variable('dbserver', 'db-port', '5432')
        pgpool.db_pgpool2_configure(c, dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable('dbserver', 'listen-address')
        if db_listen_address:
            core.sys_add_hosts(c, db_host, db_listen_address)

    geo_ip = cfg.get_variable('webserver', 'geo-ip')
    if geo_ip:
        geoip.web_geoip_install_requirements(c)
        geoip.web_geoip_install_maxmind_api(c)
        geoip.web_geoip_install_maxmind_country(c)
        geoip.web_geoip_install_maxmind_city(c)
