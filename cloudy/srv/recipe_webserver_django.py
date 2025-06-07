from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_hostname_configure, sys_add_hosts
from cloudy.sys.python import sys_python_install_common
from cloudy.web.apache import web_apache2_install_mods, web_apache2_install
from cloudy.web.supervisor import web_supervisor_install
from cloudy.web.geoip import (
    web_geoip_install_requirements,
    web_geoip_install_maxmind_api,
    web_geoip_install_maxmind_country,
    web_geoip_install_maxmind_city,
)
from cloudy.sys.firewall import fw_allow_incoming_port
from cloudy.db.pgpool import db_pgpool2_install, db_pgpool2_configure
from cloudy.web.www import web_create_data_directory
from cloudy.db.psql import db_psql_install
from cloudy.db.pgis import db_pgis_install
from cloudy.util.conf import CloudyConfig
from cloudy.srv.recipe_generic_server import srv_setup_generic_server

@task
def srv_setup_web(c: Connection, generic=True):
    """Setup a webserver database server - Ex: (cmd:[cfg-file])"""
    cfg = CloudyConfig()

    if generic:
        srv_setup_generic_server(c)

    # hostname, ips
    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        sys_hostname_configure(c, hostname)
        sys_add_hosts(c, hostname, '127.0.0.1')

    # setup python stuff
    py_version = cfg.get_variable('common', 'python-version')
    sys_python_install_common(c, py_version)

    # install webserver
    webserver = cfg.get_variable('webserver', 'webserver')
    if webserver and webserver.lower() == 'apache':
        web_apache2_install(c)
        web_apache2_install_mods(c)
    elif webserver and webserver.lower() == 'gunicorn':
        web_supervisor_install(c)

    # create web directory
    web_create_data_directory(c)

    webserver_port = cfg.get_variable('webserver', 'webserver-port')
    if webserver_port:
        fw_allow_incoming_port(c, webserver_port)

    # hostname, cache server
    cache_host = cfg.get_variable('cacheserver', 'cache-host')
    cache_listen_address = cfg.get_variable('cacheserver', 'listen-address')
    if cache_host and cache_listen_address:
        sys_add_hosts(c, cache_host, cache_listen_address)

    # create db related
    pg_version = cfg.get_variable('dbserver', 'pg-version')
    db_psql_install(c, pg_version)
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    db_pgis_install(c, pg_version, pgis_version)

    db_pgpool2_install(c)
    db_host = cfg.get_variable('dbserver', 'db-host')
    if db_host:
        db_port = cfg.get_variable('dbserver', 'db-port', '5432')
        db_pgpool2_configure(c, dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable('dbserver', 'listen-address')
        if db_listen_address:
            sys_add_hosts(c, db_host, db_listen_address)

    geo_ip = cfg.get_variable('webserver', 'geo-ip')
    if geo_ip:
        web_geoip_install_requirements(c)
        web_geoip_install_maxmind_api(c)
        web_geoip_install_maxmind_country(c)
        web_geoip_install_maxmind_city(c)









