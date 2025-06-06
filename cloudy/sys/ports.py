import os
import re
import sys
from fabric import Connection


def sys_show_next_available_port(c: Connection, start: int = 8181, max_tries: int = 50) -> int:
    """
    Show the next available TCP port starting from 'start'.
    Returns the first available port found, or -1 if none found in range.
    """
    port = start
    for _ in range(max_tries):
        result = c.run(f'netstat -lt | grep :{port}', hide=True, warn=True)
        if not result.stdout.strip():
            print(port)
            return port
        port += 1
    print(-1)
    return -1
