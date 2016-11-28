from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.aws import *
from cloudy.srv import *
from cloudy.web import *
from cloudy.util import *
from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_web(cfg_files):
    """ Setup a webserver database server - Ex: (cmd:[cfg-file])"""

    cfg = CloudyConfig(filenames=cfg_files)

    # setup generic stuff
    srv_setup_generic_server(cfg_files)

    # hostname, ips
    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')

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

    # create db related
    pg_version = cfg.get_variable('dbserver', 'pg-version')
    db_psql_install(pg_version)
    pgis_version = cfg.get_variable('dbserver', 'pgis-version')
    db_pgis_install(pg_version, pgis_version)
    sys_remove_default_startup('postgresql')

    db_pgpool2_install()
    db_host = cfg.get_variable('dbserver', 'db-host')
    if db_host:
        db_port = cfg.get_variable('dbserver', 'db-port', 5432)
        db_pgpool2_configure(dbhost=db_host, dbport=db_port)
        db_listen_address = cfg.get_variable('dbserver', 'listen-address')
        if db_listen_address:
            sys_add_hosts(db_host, db_listen_address)

    # geoIP
    web_geoip_install_requirements()
    web_geoip_install_maxmind_api()
    web_geoip_install_maxmind_country()
    web_geoip_install_maxmind_city()









