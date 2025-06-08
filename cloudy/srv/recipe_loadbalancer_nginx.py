from fabric import task
from cloudy.util.context import Context
from cloudy.sys import firewall
from cloudy.web import nginx
from cloudy.util.conf import CloudyConfig
from cloudy.srv import recipe_generic_server

@task
@Context.wrap_context
def setup_lb(c: Context, cfg_file=None, generic=True):
    """
    Setup lb server with config files
    Ex: fab setup-lb --cfg-file="./.cloudy.generic,./.cloudy.admin"
    """
    if cfg_file:
        # Split comma-separated files and pass as list
        cfg_files = [f.strip() for f in cfg_file.split(',')]
        cfg = CloudyConfig(cfg_files)
    else:
        cfg = CloudyConfig()

    if generic:
        c = recipe_generic_server.setup_server(c)

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
