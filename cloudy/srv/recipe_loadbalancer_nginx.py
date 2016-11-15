import os

from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.web import *
from cloudy.util import *

from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_lb(cfg_files):
    """
    Setup a loadbalancer - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig(filenames=cfg_files)

    srv_setup_generic_server(cfg_files)

    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')

    ssh_port = cfg.get_variable('common', 'ssh-port', 22)
    sys_firewall_install()
    sys_firewall_allow_incoming_http()
    sys_firewall_allow_incoming_https()
    sys_firewall_secure_server(ssh_port)

    # install nginx
    web_nginx_install()
    domain_name = cfg.get_variable('webserver', 'domain-name', 'example.com')
    certificate_path = cfg.get_variable('common', 'certificate-path', '~/.ssh/certificates/')
    web_nginx_copy_ssl(domain_name, certificate_path)
    webserver_private_port = cfg.get_variable('webserver', 'private-port', 8181)
    web_nginx_setup_domain(domain_name, 'https', webserver_private_port)
