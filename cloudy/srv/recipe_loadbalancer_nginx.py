"""Recipe for Nginx load balancer deployment with SSL support."""

from fabric import task

from cloudy.srv import recipe_generic_server
from cloudy.sys import firewall
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context
from cloudy.web import nginx


@task
@Context.wrap_context
def setup_lb(c: Context, cfg_paths=None, generic=True):
    """
    Setup Nginx load balancer with SSL support.

    Installs and configures Nginx as a reverse proxy load balancer with
    HTTP/HTTPS support, SSL certificate management, and upstream server
    configuration for high-availability web applications.

    Args:
        cfg_paths: Comma-separated config file paths
        generic: Whether to run generic server setup first

    Example:
        fab recipe.lb-install --cfg-paths="./.cloudy.generic,./.cloudy.lb"
    """
    cfg = CloudyConfig(cfg_paths)

    if generic:
        c = recipe_generic_server.setup_server(c, cfg_paths)

    firewall.fw_allow_incoming_http(c)
    firewall.fw_allow_incoming_https(c)

    # install nginx
    nginx.web_nginx_install(c)
    protocol = "http"
    domain_name = cfg.get_variable("webserver", "domain-name", "example.com")
    certificate_path = cfg.get_variable("common", "certificate-path")
    if certificate_path:
        nginx.web_nginx_copy_ssl(c, domain_name, certificate_path)
        protocol = "https"

    binding_address = cfg.get_variable("webserver", "binding-address", "*")
    upstream_address = cfg.get_variable("webserver", "upstream-address")
    upstream_port = cfg.get_variable("webserver", "upstream-port", "8181")
    if upstream_address and upstream_port:
        nginx.web_nginx_setup_domain(
            c, domain_name, protocol, binding_address, upstream_address, upstream_port
        )

    # Success message
    print("\n🎉 ✅ NGINX LOAD BALANCER SETUP COMPLETED SUCCESSFULLY!")
    print("📋 Configuration Summary:")
    print(f"   └── Domain: {domain_name}")
    print(f"   └── Protocol: {protocol.upper()}")
    print(f"   └── Binding Address: {binding_address}")
    if upstream_address and upstream_port:
        print(f"   └── Upstream: {upstream_address}:{upstream_port}")
    if certificate_path:
        print("   └── SSL Certificate: Configured")
    print("   └── Firewall: HTTP (80) and HTTPS (443) allowed")
    print("\n🚀 Nginx load balancer is ready to serve traffic!")
    if generic:
        admin_user = cfg.get_variable("common", "admin-user", "admin")
        ssh_port = cfg.get_variable("common", "ssh-port", "22")
        print(f"   └── Admin SSH: {admin_user}@server:{ssh_port}")
    print(f"\n🌍 Access your site at: {protocol}://{domain_name}")
