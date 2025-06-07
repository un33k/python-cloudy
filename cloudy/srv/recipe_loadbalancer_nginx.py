from fabric import Connection, task
from cloudy.sys import firewall
from cloudy.web import nginx
from cloudy.util.conf import CloudyConfig
from cloudy.srv import recipe_generic_server

@task
def srv_setup_lb(c: Connection, generic=True):
    """
    Setup a loadbalancer - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        recipe_generic_server.srv_setup_generic_server(c)

    firewall.fw_allow_incoming_http(c)
    firewall.fw_allow_incoming_https(c)

    # install nginx
    nginx.web_nginx_install(c)
    protocol = 'http'
    domain_name = cfg.get_variable('webserver', 'domain-name', 'example.com')
    certificate_path = cfg.get_variable('common', 'certificate-path')
    if certificate_path:
        nginx.web_nginx_copy_ssl(c, domain_name, certificate_path)
        protocol = 'https'

    binding_address = cfg.get_variable('webserver', 'binding-address', '*')
    upstream_address = cfg.get_variable('webserver', 'upstream-address')
    upstream_port = cfg.get_variable('webserver', 'upstream-port', '8181')
    if upstream_address and upstream_port:
        nginx.web_nginx_setup_domain(c, domain_name, protocol, binding_address, upstream_address, upstream_port)
