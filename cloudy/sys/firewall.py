from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit

@task
def fw_reload_ufw(c: Connection) -> None:
    """Helper to reload and show UFW status."""
    c.sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')

@task
def fw_install(c: Connection) -> None:
    """Install UFW firewall."""
    c.sudo('apt -y install ufw')
    sys_etc_git_commit(c, 'Installed firewall (ufw)')

@task
def fw_secure_server(c: Connection, ssh_port: str = '22') -> None:
    """Secure the server: deny all incoming, allow outgoing, allow SSH."""
    c.sudo('ufw logging on')
    c.sudo('ufw default deny incoming')
    c.sudo('ufw default allow outgoing')
    c.sudo(f'ufw allow {ssh_port}')
    fw_reload_ufw(c)
    sys_etc_git_commit(c, 'Server is secured down')

@task
def fw_wide_open(c: Connection) -> None:
    """Open up firewall: allow all incoming and outgoing."""
    c.sudo('ufw default allow incoming')
    c.sudo('ufw default allow outgoing')
    fw_reload_ufw(c)

@task
def fw_disable(c: Connection) -> None:
    """Disable firewall."""
    c.sudo('ufw disable; sudo ufw status verbose')

@task
def fw_allow_incoming_http(c: Connection) -> None:
    """Allow HTTP (port 80) requests."""
    c.sudo('ufw allow http')
    fw_reload_ufw(c)

@task
def fw_disallow_incoming_http(c: Connection) -> None:
    """Disallow HTTP (port 80) requests."""
    c.sudo('ufw delete allow http')
    fw_reload_ufw(c)

@task
def fw_allow_incoming_https(c: Connection) -> None:
    """Allow HTTPS (port 443) requests."""
    c.sudo('ufw allow https')
    fw_reload_ufw(c)

@task
def fw_disallow_incoming_https(c: Connection) -> None:
    """Disallow HTTPS (port 443) requests."""
    c.sudo('ufw delete allow https')
    fw_reload_ufw(c)

@task
def fw_allow_incoming_postgresql(c: Connection) -> None:
    """Allow PostgreSQL (port 5432) requests."""
    c.sudo('ufw allow postgresql')
    fw_reload_ufw(c)

@task
def fw_disallow_incoming_postgresql(c: Connection) -> None:
    """Disallow PostgreSQL (port 5432) requests."""
    c.sudo('ufw delete allow postgresql')
    fw_reload_ufw(c)

@task
def fw_allow_incoming_port(c: Connection, port: int) -> None:
    """Allow requests on a specific port."""
    c.sudo(f'ufw allow {port}')
    fw_reload_ufw(c)

@task
def fw_disallow_incoming_port(c: Connection, port: int) -> None:
    """Disallow requests on a specific port."""
    c.sudo(f'ufw delete allow {port}')
    c.sudo(f'ufw delete allow {port}/tcp', warn=True)
    c.sudo(f'ufw delete allow {port}/udp', warn=True)
    fw_reload_ufw(c)

@task
def fw_allow_incoming_port_proto(c: Connection, port: int, proto: str) -> None:
    """Allow requests on a specific port/protocol."""
    c.sudo(f'ufw allow {port}/{proto}')
    fw_reload_ufw(c)

@task
def fw_disallow_incoming_port_proto(c: Connection, port: int, proto: str) -> None:
    """Disallow requests on a specific port/protocol."""
    c.sudo(f'ufw delete allow {port}/{proto}')
    fw_reload_ufw(c)

@task
def fw_allow_incoming_host_port(c: Connection, host: str, port: int) -> None:
    """Allow requests from a specific host on a specific port."""
    c.sudo(f'ufw allow from {host} to any port {port}')
    fw_reload_ufw(c)

@task
def fw_disallow_incoming_host_port(c: Connection, host: str, port: int) -> None:
    """Disallow requests from a specific host on a specific port."""
    c.sudo(f'ufw delete allow from {host} to any port {port}')
    fw_reload_ufw(c)
