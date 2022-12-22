import os
from cloudy.db import *
from cloudy.sys import *
from cloudy.util import *
from fabric.api import env


def srv_setup_generic_server():
    """
    Setup a generic server with the required packages - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        sys_hostname_configure(hostname)
        sys_add_hosts(hostname, '127.0.0.1')

    sys_set_ipv4_precedence()

    # git info
    sys_git_install()
    git_user_full_name = cfg.get_variable('common', 'git-user-full-name')
    git_user_email = cfg.get_variable('common', 'git-user-email')
    if git_user_full_name and git_user_email:
        sys_git_configure('root', git_user_full_name, git_user_email)

    sys_update()
    sys_install_common()
    sys_time_install_common()

    sys_install_postfix()
    sys_set_default_editor()

    # timezone and locale
    timezone = cfg.get_variable('common', 'timezone', 'America/New_York')
    sys_configure_timezone(timezone)
    locale = cfg.get_variable('common', 'locale', 'en_US.UTF-8')
    sys_locale_configure()

    # swap
    swap = cfg.get_variable('common', 'swap-size')
    if swap:
        sys_swap_configure(swap)

    # users & passwords
    admin_user = cfg.get_variable('common', 'admin-user')
    admin_pass = cfg.get_variable('common', 'admin-pass')
    admin_group = cfg.get_variable('common', 'admin-group', 'admin')
    if admin_user and admin_pass:
        sys_user_add(admin_user)
        sys_user_change_password(admin_user, admin_pass)
        sys_user_add_sudoer(admin_user)
        sys_user_set_group_umask(admin_user)
        sys_user_create_group(admin_group)
        sys_user_add_to_group(admin_user, admin_group)
        sys_user_create_group('www-data')
        sys_user_add_to_group(admin_user, 'www-data')

        shared_key_dir = cfg.get_variable('common', 'shared-key-path')
        if shared_key_dir:
            sys_ssh_push_server_shared_keys(admin_user, shared_key_dir)

    # ssh stuff
    sys_firewall_install()
    ssh_port = cfg.get_variable('common', 'ssh-port', 22)
    if ssh_port:
        sys_ssh_set_port(ssh_port)
        sys_firewall_secure_server(ssh_port)

    disable_root = cfg.get_variable('common', 'ssh-disable-root')
    if disable_root and disable_root.upper() == 'YES':
        sys_ssh_disable_root_login()

    enable_password = cfg.get_variable('common', 'ssh-enable-password')
    if enable_password and enable_password.upper() == 'YES':
        sys_ssh_enable_password_authentication()

    pub_key = cfg.get_variable('common', 'ssh-key-path')
    if pub_key:
        pub_key = os.path.expanduser(pub_key)
        if os.path.exists(pub_key):
            if admin_user:
                sys_ssh_push_public_key(admin_user, pub_key)






