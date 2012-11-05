from cloudy.db import *
from cloudy.sys import *
from cloudy.aws import *
from cloudy.srv import *
from cloudy.util import 
from fabric.api import env


def setup_db_postgres_primary(cfg_files='~/.cloudy'):
    cfg = CloudyConfig(filenames=cfg_files)
    
    # git info
    git_username = c.get_variable('common', 'git-username')
    git_email = c.get_variable('common', 'git-email')
    git_enabled_users = c.get_variable('common', 'git-enabled-users')

    # timezone and locale
    timezone = c.get_variable('common', 'timezone', 'Canada/Eastern')
    locale = c.get_variable('common', 'locale', 'en_US.UTF-8')

    # users & passwords
    admin_user = c.get_variable('pg_master', 'user')
    admin_pass = c.get_variable('pg_master', 'pass')
    admin_group = c.get_variable('pg_master', 'www-data')
    postgres_user_pass = c.get_variable('pg_master', 'pg-pass')

    # hostname, ips
    hostname = c.get_variable('pg_master', 'hostname', 'nw-db1')
    
    # posgresql: version, cluster, data_dir
    pg_version = c.get_variable('pg_master', 'pg-version')
    pg_cluster = c.get_variable('pg_master', 'pg-cluster')
    pg_data_dir = c.get_variable('pg_master', 'pg-data-dir')

    # pgis version
    pgis_version = c.get_variable('pg_master', 'pgis-version')







