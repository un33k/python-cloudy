from fabric import Connection, task
from cloudy.sys.etc import sys_etc_git_commit

@task
def sys_python_install_common(c: Connection, py_version: str = '3.8') -> None:
    """Install common python application packages."""
    major = py_version.split('.')[0]
    if major == '2':
        major = ''
    requirements = ' '.join([
        f'python{major}-dev',
        f'python{major}-setuptools',
        f'python{major}-psycopg2',
        f'python{major}-pip',
        f'python{major}-pil',
        'python-dev',
        'python-virtualenv',
        'libfreetype6-dev',
        'libjpeg62-dev',
        'libpng12-dev',
        'zlib1g-dev',
        'liblcms2-dev',
        'libwebp-dev',
        'tcl8.5-dev',
        'tk8.5-dev',
        'gettext',
    ])
    c.sudo(f'apt -y install {requirements}')
    if major == '2':
        c.sudo('pip install pillow')
    else:
        c.sudo('pip3 install pillow')
    sys_etc_git_commit(c, 'Installed common python packages')



