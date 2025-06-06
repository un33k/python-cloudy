import time
from fabric import Connection, task

def sys_start_service(c: Connection, service: str) -> None:
    """Start a systemd service."""
    c.sudo(f'systemctl start {service}')

def sys_stop_service(c: Connection, service: str) -> None:
    """Stop a systemd service."""
    c.sudo(f'systemctl stop {service}')

def sys_reload_service(c: Connection, service: str) -> None:
    """Reload a systemd service."""
    c.sudo(f'systemctl reload {service}')

def sys_restart_service(c: Connection, service: str) -> None:
    """Restart a systemd service safely."""
    c.sudo(f'systemctl stop {service}', warn=True)
    time.sleep(2)
    c.sudo(f'systemctl start {service}')
    time.sleep(2)
