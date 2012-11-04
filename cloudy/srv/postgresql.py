import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.db.psql import *
from cloudy.db.pgis import *
from cloudy.sys import *


def srv_postgresql_install(version, gisversion='', data_dir='/data/postgresql', cluster='main'):
    db_psql_install(version)
    db_psql_make_data_dir(version, data_dir)
    db_psql_remove_cluster(version, cluster)
    db_psql_create_cluster(version=version, cluster=cluster, data_dir=data_dir)
    db_psql_configure(version=version)
    db_psql_postgres_password('new2day')
    db_pgis_install(version)
    db_pgis_configure(version, gisversion)
    db_pgis_get_database_gis_info('template_postgis')


def srv_postgresql_server_setup():
    """ Update package repositories - Ex: (cmd)"""
    
    sys_update()
    sys_safe_upgrade()
    sys_install_common()
    sys_configure_timezone('Canada/Eastern')
    sys_git_configure('root', 'Val Neekman', 'val@neekware.com')
    sys_hostname_configure('nw-db1')
    sys_add_hosts('nw-db1', '127.0.0.1')
    sys_locale_configure()
    sys_install_postfix()
    sys_security_install_common()
    users = ['vman', 'admino']
    for user in users:
        sys_user_add(user)
        sys_user_add_sudoer(user)
        sys_user_add_to_group(user, 'www-data')
        sys_user_set_group_umask(user)










