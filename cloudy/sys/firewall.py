from fabric import task
from cloudy.util.context import Context
from cloudy.sys.etc import sys_etc_git_commit

@task
@Context.wrap_context
def fw_reload_ufw(c: Context) -> None:
    """Helper to reload and show UFW status."""
    c.sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')

@task
@Context.wrap_context
def fw_install(c: Context) -> None:
    """Install UFW firewall."""
    c.sudo('apt -y install ufw')
    sys_etc_git_commit(c, 'Installed firewall (ufw)')

@task
@Context.wrap_context
def fw_secure_server(c: Context, ssh_port: str = '22') -> None:
    """Secure the server: deny all incoming, allow outgoing, allow SSH."""
    c.sudo('ufw logging on')
    c.sudo('ufw default deny incoming')
    c.sudo('ufw default allow outgoing')
    c.sudo(f'ufw allow {ssh_port}')
    fw_reload_ufw(c)
    sys_etc_git_commit(c, 'Server is secured down')

@task
@Context.wrap_context
def fw_wide_open(c: Context) -> None:
    """Open up firewall: allow all incoming and outgoing."""
    c.sudo('ufw default allow incoming')
    c.sudo('ufw default allow outgoing')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disable(c: Context) -> None:
    """Disable firewall."""
    c.sudo('ufw disable; sudo ufw status verbose')

@task
@Context.wrap_context
def fw_allow_incoming_http(c: Context) -> None:
    """Allow HTTP (port 80) requests."""
    c.sudo('ufw allow http')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disallow_incoming_http(c: Context) -> None:
    """Disallow HTTP (port 80) requests."""
    c.sudo('ufw delete allow http')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_allow_incoming_https(c: Context) -> None:
    """Allow HTTPS (port 443) requests."""
    c.sudo('ufw allow https')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disallow_incoming_https(c: Context) -> None:
    """Disallow HTTPS (port 443) requests."""
    c.sudo('ufw delete allow https')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_allow_incoming_postgresql(c: Context) -> None:
    """Allow PostgreSQL (port 5432) requests."""
    c.sudo('ufw allow postgresql')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disallow_incoming_postgresql(c: Context) -> None:
    """Disallow PostgreSQL (port 5432) requests."""
    c.sudo('ufw delete allow postgresql')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_allow_incoming_port(c: Context, port: str) -> None:
    """Allow requests on a specific port."""
    c.sudo(f'ufw allow {port}')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disallow_incoming_port(c: Context, port: int) -> None:
    """Disallow requests on a specific port."""
    c.sudo(f'ufw delete allow {port}')
    c.sudo(f'ufw delete allow {port}/tcp', warn=True)
    c.sudo(f'ufw delete allow {port}/udp', warn=True)
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_allow_incoming_port_proto(c: Context, port: str, proto: str) -> None:
    """Allow requests on a specific port/protocol."""
    c.sudo(f'ufw allow {port}/{proto}')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disallow_incoming_port_proto(c: Context, port: int, proto: str) -> None:
    """Disallow requests on a specific port/protocol."""
    c.sudo(f'ufw delete allow {port}/{proto}')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_allow_incoming_host_port(c: Context, host: str, port: int) -> None:
    """Allow requests from a specific host on a specific port."""
    c.sudo(f'ufw allow from {host} to any port {port}')
    fw_reload_ufw(c)

@task
@Context.wrap_context
def fw_disallow_incoming_host_port(c: Context, host: str, port: int) -> None:
    """Disallow requests from a specific host on a specific port."""
    c.sudo(f'ufw delete allow from {host} to any port {port}')
    fw_reload_ufw(c)
