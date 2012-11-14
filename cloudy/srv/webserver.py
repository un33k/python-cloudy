from cloudy.db import *
from cloudy.sys import *
from cloudy.aws import *
from cloudy.srv import *
from cloudy.web import *
from cloudy.util import *
from cloudy.srv.generic import setup_generic_server
from fabric.api import env

def srv_setup_web_server(cfg_files='~/.cloudy'):
    """ Setup a webserver database server - Ex: (cmd:[cfg-file])"""
    
    cfg = CloudyConfig(filenames=cfg_files)
    
    # setup generic stuff
    setup_generic_server()
   
    # hostname, ips
    hostname = cfg.get_variable('webserver', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')

    # setup python stuff
    sys_python_install_common()
    web_install_common()
    
    # install cache daemon
    sys_memcached_install()
    sys_memcached_configure_memory()
    sys_memcached_configure_interface()

    # create web directory
    web_create_data_directory()
    db_psql_install()
    db_pgis_install()
    sys_remove_default_startup('postgresql')
    db_pgpool2_install()
    db_host = cfg.get_variable('webserver', 'db-host')
    if db_host:
        db_pgpool2_configure(db_host)
        db_listen_address = cfg.get_variable('webserver', 'listen-address')
        if db_listen_address:
            sys_add_hosts(db_host, db_listen_address)

    sys_shutdown()

