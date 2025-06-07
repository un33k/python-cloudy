import sys
from fabric import task
from cloudy.util.context import Context
from cloudy.sys.etc import sys_etc_git_commit

@task
@Context.wrap_context
def sys_swap_configure(c: Context, size: str = '512') -> None:
    """
    Create and install a swap file of the given size in MB.
    """
    swap_file = f'/swap/{size}MiB.swap'
    c.sudo('mkdir -p /swap')
    # Check if swap file exists
    result = c.run(f'test -e {swap_file}', warn=True)
    if result.failed:
        c.sudo(f'fallocate -l {size}m {swap_file}')
        c.sudo(f'chmod 600 {swap_file}')
        c.sudo(f'mkswap {swap_file}')
        c.sudo(f'swapon {swap_file}')
        c.sudo(f'echo "{swap_file} swap  swap  defaults  0 0" | sudo tee -a /etc/fstab')
        sys_etc_git_commit(c, f'Added swap file ({swap_file})')
    else:
        print(f'Swap file ({swap_file}) exists', file=sys.stderr)
