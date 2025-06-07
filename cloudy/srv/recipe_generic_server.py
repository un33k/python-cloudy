import os
import uuid
from fabric import Connection, task
from cloudy.sys import core, timezone, swap, postfix, vim, ssh, firewall, user
from cloudy.util.conf import CloudyConfig

@task
def setup_server(c: Connection) -> None:
    """
    Setup a generic server with the required packages - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()
    
    # git info
    core.sys_init(c)
    core.sys_update(c)

    git_user_full_name = cfg.get_variable('common', 'git-user-full-name')
    git_user_email = cfg.get_variable('common', 'git-user-email')
    if git_user_full_name and git_user_email:
        core.sys_git_configure(c, 'root', git_user_full_name, git_user_email)

    hostname = cfg.get_variable('common', 'hostname')
    if hostname:
        core.sys_hostname_configure(c, hostname)
        core.sys_add_hosts(c, hostname, '127.0.0.1')

    core.sys_set_ipv4_precedence(c)
    core.sys_install_common(c)
    timezone.sys_time_install_common(c)
    postfix.sys_install_postfix(c)
    vim.sys_set_default_editor(c)

    # timezone and locale
    tz = cfg.get_variable('common', 'timezone', 'America/New_York')
    timezone.sys_configure_timezone(c, tz)
    locale_val = cfg.get_variable('common', 'locale', 'en_US.UTF-8')
    core.sys_locale_configure(c, locale_val)

    # swap
    swap_size = cfg.get_variable('common', 'swap-size')
    if swap_size:
        swap.sys_swap_configure(c, swap_size)

    # primary users & passwords
    admin_user = cfg.get_variable('common', 'admin-user')
    admin_pass = cfg.get_variable('common', 'admin-pass')
    admin_groups = cfg.get_variable('common', 'admin-groups', 'admin,www-data')
    if admin_user and admin_pass:
        user.sys_user_add(c, admin_user)
        user.sys_user_change_password(c, admin_user, admin_pass)
        user.sys_user_add_sudoer(c, admin_user)
        user.sys_user_set_group_umask(c, admin_user)
        user.sys_user_create_groups(c, admin_groups)
        user.sys_user_add_to_groups(c, admin_user, admin_groups)
        shared_key_dir = cfg.get_variable('common', 'shared-key-path')
        if shared_key_dir:
            ssh.sys_ssh_push_server_shared_keys(c, admin_user, shared_key_dir)

    # automation users & passwords
    auto_user = cfg.get_variable('common', 'auto-user')
    auto_pass = cfg.get_variable('common', 'auto-pass', uuid.uuid4().hex)
    auto_groups = cfg.get_variable('common', 'auto-groups', 'admin,www-data')
    if auto_user and auto_pass:
        user.sys_user_add(c, auto_user)
        user.sys_user_change_password(c, auto_user, auto_pass)
        user.sys_user_add_sudoer(c, auto_user)
        user.sys_user_set_group_umask(c, auto_user)
        user.sys_user_create_groups(c, auto_groups)
        user.sys_user_add_to_groups(c, auto_user, auto_groups)
        shared_key_dir = cfg.get_variable('common', 'shared-key-path')
        if shared_key_dir:
            ssh.sys_ssh_push_server_shared_keys(c, auto_user, shared_key_dir)

    # ssh stuff
    firewall.fw_install(c)
    ssh_port = cfg.get_variable('common', 'ssh-port', '22')
    if ssh_port:
        ssh.sys_ssh_set_port(c, ssh_port)
        firewall.fw_secure_server(c, ssh_port)

    disable_root = cfg.get_variable('common', 'ssh-disable-root')
    if disable_root and disable_root.upper() == 'YES':
        ssh.sys_ssh_disable_root_login(c)

    enable_password = cfg.get_variable('common', 'ssh-enable-password')
    if enable_password and enable_password.upper() == 'YES':
        ssh.sys_ssh_enable_password_authentication(c)

    pub_key = cfg.get_variable('common', 'ssh-key-path')
    if pub_key:
        pub_key = os.path.expanduser(pub_key)
        if os.path.exists(pub_key) and admin_user:
            ssh.sys_ssh_push_public_key(c, admin_user, pub_key)






