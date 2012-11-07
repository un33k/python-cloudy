from cloudy.db import *
from cloudy.sys import *
from cloudy.aws import *
from cloudy.srv import *
from cloudy.util import *
from fabric.api import env
import logging

logging.getLogger().setLevel(logging.WARNING)

def setup_db_postgres_primary(cfg_files='~/.cloudy'):
    cfg = CloudyConfig(filenames=cfg_files)
    sys_update()
    sys_install_common()
    
    # git info
    git_user_full_name = cfg.get_variable('common', 'git-user-full-name')
    git_user_email = cfg.get_variable('common', 'git-user-email')
    if git_user_full_name and git_user_email:
        sys_git_configure('root', git_user_full_name, git_user_email)

    sys_safe_upgrade()
    sys_install_postfix()
    sys_security_install_common()
    sys_set_default_editor()
    
    # timezone and locale
    timezone = cfg.get_variable('common', 'timezone', 'Canada/Eastern')
    locale = cfg.get_variable('common', 'locale', 'en_US.UTF-8')
    sys_configure_timezone(timezone)
    sys_locale_configure()


    # swap
    swap = cfg.get_variable('ps_master', 'swap-size')
    if swap:
        sys_swap_configure(swap)

    # hostname, ips
    hostname = cfg.get_variable('pg_master', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')


    # users & passwords
    admin_user = cfg.get_variable('pg_master', 'admin-user')
    admin_pass = cfg.get_variable('pg_master', 'admin-pass')
    admin_group = cfg.get_variable('pg_master', 'admin-group', 'admin')
    if admin_user and admin_pass:
        sys_user_add(admin_user)
        sys_user_change_password(admin_user, admin_pass)
        sys_user_add_sudoer(admin_user)
        sys_user_set_group_umask(admin_user)
        sys_user_create_group(admin_group)
        sys_user_add_to_group(admin_user, admin_group)
        if git_user_full_name and git_user_email:
            sys_git_configure(admin_user, git_user_full_name, git_user_email)


    # posgresql: version, cluster, data_dir
    pg_version = cfg.get_variable('pg_master', 'pg-version')
    pg_cluster = cfg.get_variable('pg_master', 'pg-cluster', 'main')
    pg_encoding = cfg.get_variable('pg_master', 'pg-encoding', 'UTF-8')
    pg_data_dir = cfg.get_variable('pg_master', 'pg-data-dir', '/var/lib/postgresql')

    db_psql_install(pg_version)
    db_psql_make_data_dir(pg_version, pg_data_dir)
    db_psql_remove_cluster(pg_version, pg_cluster)
    db_psql_create_cluster(pg_version, pg_cluster, pg_encoding, pg_data_dir)
    db_psql_configure(pg_version)
    
    # change postgres' user password
    postgres_user_pass = cfg.get_variable('pg_master', 'postgres-pass')
    if postgres_user_pass:
        db_psql_postgres_password(postgres_user_pass)

    # pgis version
    pgis_version = cfg.get_variable('pg_master', 'pgis-version')
    if pgis_version:
        db_pgis_install(pg_version)
        db_pgis_configure(pg_version, pgis_version)
        db_pgis_get_database_gis_info('template_postgis')


def setup_webserver(cfg_files='~/.cloudy'):
    cfg = CloudyConfig(filenames=cfg_files)
    sys_update()
    sys_install_common()

    # git info
    git_user_full_name = cfg.get_variable('common', 'git-user-full-name')
    git_user_email = cfg.get_variable('common', 'git-user-email')
    if git_user_full_name and git_user_email:
        sys_git_configure('root', git_user_full_name, git_user_email)


    sys_safe_upgrade()
    sys_install_postfix()
    sys_security_install_common()
    sys_memcached_install()
    sys_memcached_configure_interface()
    sys_python_install_common()
    sys_set_default_editor()

    # timezone and locale
    timezone = cfg.get_variable('common', 'timezone', 'Canada/Eastern')
    locale = cfg.get_variable('common', 'locale', 'en_US.UTF-8')
    sys_configure_timezone(timezone)
    sys_locale_configure()

    # swap
    swap = cfg.get_variable('webserver', 'swap-size')
    if swap:
        sys_swap_configure(swap)

    # hostname, ips
    hostname = cfg.get_variable('webserver', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')


    # users & passwords
    admin_user = cfg.get_variable('webserver', 'admin-user')
    admin_pass = cfg.get_variable('webserver', 'admin-pass')
    admin_group = cfg.get_variable('webserver', 'admin-group', 'admin')
    if admin_user and admin_pass:
        sys_user_add(admin_user)
        sys_user_change_password(admin_user, admin_pass)
        sys_user_add_sudoer(admin_user)
        sys_user_set_group_umask(admin_user)
        sys_user_create_group(admin_group)
        sys_user_add_to_group(admin_user, admin_group)
        if git_user_full_name and git_user_email:
            sys_git_configure(admin_user, git_user_full_name, git_user_email)

        
        




