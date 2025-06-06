import time
from fabric.api import sudo, settings

def sys_start_service(service: str) -> None:
    """Start a systemd service."""
    sudo(f'systemctl start {service}')

def sys_stop_service(service: str) -> None:
    """Stop a systemd service."""
    sudo(f'systemctl stop {service}')

def sys_reload_service(service: str) -> None:
    """Reload a systemd service."""
    sudo(f'systemctl reload {service}')

def sys_restart_service(service: str) -> None:
    """Restart a systemd service safely."""
    with settings(warn_only=True):
        sudo(f'systemctl stop {service}')
    time.sleep(2)
    sudo(f'systemctl start {service}')
    time.sleep(2)
