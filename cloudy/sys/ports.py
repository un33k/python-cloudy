import os
import re
import sys

from fabric.api import run, settings, hide


def sys_show_next_available_port(start: int = 8181, max_tries: int = 50) -> int:
    """
    Show the next available TCP port starting from 'start'.
    Returns the first available port found, or -1 if none found in range.
    """
    port = start
    for _ in range(max_tries):
        with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            port_in_use = run(f'netstat -lt | grep :{port}')
            if not port_in_use:
                print(port)
                return port
            port += 1
    print(-1)
    return -1
