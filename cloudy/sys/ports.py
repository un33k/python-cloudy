import sys
from fabric import task
from cloudy.util.context import Context

@task
@Context.wrap_context
def sys_show_next_available_port(c: Context, start: str = '8181', max_tries: str = '50') -> str:
    """
    Show the next available TCP port starting from 'start'.
    Returns the first available port found, or -1 if none found in range.
    """
    port = start
    for _ in range(int(max_tries)):
        result = c.run(f'netstat -lt | grep :{port}', hide=True, warn=True)
        if not result.stdout.strip():
            print(port)
            return port
        port = str(int(port) + 1)
    print(f"No available port found starting from {start}", file=sys.stderr)
    return '-1'
