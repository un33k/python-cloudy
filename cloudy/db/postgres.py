import os
import re
import sys
from operator import itemgetter

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide


def _psql_latest_version():
    """ Get the latest postgres version """
    
    latest_version = '9.1'
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
            ret = run('apt-cache search postgresql-client')
    
    version_re = re.compile('postgresql-client-([0-9.]*)\s-')
    lines = ret.split('\n')
    versions = []
    for line in lines:
        print line
        ver = version_re.search(line.lower())
        if ver:
            versions.append(ver.group(1))
    
    versions.sort(key = itemgetter(2), reverse = False)
    try:
        latest_version = versions[0]
    except:
        pass
    return latest_version


def psql_latest_version():
    """ Print the latest postgres version """
    
    ver = _psql_latest_version()
    print >> sys.stderr, ver


def psql_install(version=''):
    """ Install postgres of a given version or the latest version """
    if not version:
        version = _psql_latest_version()
        
    # requirements
    requirements = '%s' % ' '.join([
        'postgresql-{0}'.format(version),
        'postgresql-client-{0}'.format(version),
        'postgresql-contrib-{0}'.format(version),
        'postgresql-server-dev-{0}'.format(version),
        'postgresql-client-common',
        'binutils'
    ])
    
    # install requirements
    cmd = 'apt-get -y install'
    sudo('{0} {1}'.format(cmd, requirements))
    return

def psql_configure(version='9.1', data_dir=''):
    if os.path.exists(data_dir):
        pass










