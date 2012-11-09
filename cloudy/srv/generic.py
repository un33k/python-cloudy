from cloudy.db import *
from cloudy.sys import *
from cloudy.util import *
from fabric.api import env

def setup_generic_server(cfg_files='~/.cloudy'):
    cfg = CloudyConfig(filenames=cfg_files)
    sys_update()
    sys_install_common()
    sys_time_install_common()
    sys_add_chkconfig()

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



