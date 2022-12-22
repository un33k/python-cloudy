import os

from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.web import *
from cloudy.util import *

from cloudy.srv.recipe_generic_server import srv_setup_generic_server


def srv_setup_lb(generic=True):
    """
    Setup a loadbalancer - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        srv_setup_generic_server()

    sys_firewall_allow_incoming_http()
    sys_firewall_allow_incoming_https()

    # install nginx
    web_nginx_install()
    protocol = 'http'
    domain_name = cfg.get_variable('webserver', 'domain-name', 'example.com')
    certificate_path = cfg.get_variable('common', 'certificate-path')
    if certificate_path:
        web_nginx_copy_ssl(domain_name, certificate_path)
        protocol = 'https'

    binding_address = cfg.get_variable('webserver', 'binding-address', '*')
    upstream_address = cfg.get_variable('webserver', 'upstream-address')
    upstream_port = cfg.get_variable('webserver', 'upstream-port', 8181)
    if upstream_address and upstream_port:
        web_nginx_setup_domain(domain_name, protocol, binding_address, upstream_address, upstream_port)
