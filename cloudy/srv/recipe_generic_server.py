import os
import uuid
from typing import Optional

from fabric import task

from cloudy.sys import core, firewall, postfix, ssh, swap, timezone, user, vim
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context


@task
@Context.wrap_context
def setup_server(c: Context, cfg_file: Optional[str] = None) -> Context:
    """
    Setup a generic server with comprehensive configuration.

    This recipe performs a complete server setup including:
    - System initialization and updates
    - Git configuration
    - Hostname and network setup
    - User creation (admin and automation users)
    - SSH security configuration
    - Firewall setup
    - Timezone and locale configuration
    - Swap configuration
    - Essential package installation

    Args:
        cfg_file: Comma-separated list of config files to use

    Returns:
        Updated Context object (may have new connection settings)

    Example:
        fab recipe.gen-install --cfg-file="./.cloudy.generic,./.cloudy.admin"
    """
    # Initialize configuration
    if cfg_file:
        cfg_files = [f.strip() for f in cfg_file.split(",")]
        cfg = CloudyConfig(cfg_files)
    else:
        cfg = CloudyConfig()

    # Read all configuration values upfront
    git_user_full_name = cfg.get_variable("common", "git-user-full-name")
    git_user_email = cfg.get_variable("common", "git-user-email")
    hostname = cfg.get_variable("common", "hostname")
    timezone_val = cfg.get_variable("common", "timezone", "America/New_York")
    locale_val = cfg.get_variable("common", "locale", "en_US.UTF-8")
    swap_size = cfg.get_variable("common", "swap-size")

    # User configuration
    admin_user = cfg.get_variable("common", "admin-user")
    admin_pass = cfg.get_variable("common", "admin-pass")
    admin_groups = cfg.get_variable("common", "admin-groups", "admin,www-data")

    auto_user = cfg.get_variable("auto", "auto-user")
    auto_pass = cfg.get_variable("auto", "auto-pass", uuid.uuid4().hex)
    auto_groups = cfg.get_variable("auto", "auto-groups", "admin,www-data")

    # SSH and security configuration
    ssh_port = cfg.get_variable("common", "ssh-port", "22")
    disable_root = cfg.get_boolean_config("common", "ssh-disable-root")
    enable_password = cfg.get_boolean_config("common", "ssh-enable-password")
    pub_key = cfg.get_variable("common", "ssh-key-path")

    # Validate configuration values
    user.validate_user_config(admin_user, admin_pass)
    ssh.validate_ssh_config(ssh_port)

    # === SYSTEM INITIALIZATION ===
    core.sys_init(c)
    core.sys_update(c)

    # Configure git if credentials provided
    if git_user_full_name and git_user_email:
        core.sys_git_configure(c, "root", git_user_full_name, git_user_email)

    # Configure hostname if provided
    if hostname:
        core.sys_hostname_configure(c, hostname)
        core.sys_add_hosts(c, hostname, "127.0.0.1")

    # Install essential packages and configure system
    core.sys_set_ipv4_precedence(c)
    core.sys_install_common(c)
    timezone.sys_time_install_common(c)
    postfix.sys_install_postfix(c)
    vim.sys_set_default_editor(c)

    # Configure timezone and locale
    timezone.sys_configure_timezone(c, timezone_val)
    core.sys_locale_configure(c, locale_val)

    # Configure swap if specified
    if swap_size:
        swap.sys_swap_configure(c, swap_size)

    # === USER CREATION ===
    # Create admin user with full setup
    admin_shared_key_dir = cfg.get_variable("common", "shared-key-path")
    user.sys_user_create_with_setup(c, admin_user, admin_pass, admin_groups, admin_shared_key_dir)

    # Create automation user with full setup
    auto_shared_key_dir = cfg.get_variable("auto", "shared-key-path")
    user.sys_user_create_with_setup(c, auto_user, auto_pass, auto_groups, auto_shared_key_dir)

    # === SSH & SECURITY CONFIGURATION ===
    # Install and configure firewall
    firewall.fw_install(c)

    # Configure SSH port and secure server
    if ssh_port != "22":
        ssh.sys_ssh_set_port(c, ssh_port)
        c = c.reconnect(new_port=ssh_port)

    firewall.fw_secure_server(c, ssh_port)
    c = c.reconnect(new_port=ssh_port)

    # Enable password authentication if requested (before disabling root)
    if enable_password:
        ssh.sys_ssh_enable_password_authentication(c)

    # Install public key for admin user BEFORE disabling root login
    if pub_key and admin_user:
        pub_key_path = os.path.expanduser(pub_key)
        if os.path.exists(pub_key_path):
            ssh.sys_ssh_push_public_key(c, admin_user, pub_key_path)

    # Disable root login if configured and admin user exists with SSH key
    if admin_user and disable_root and pub_key:
        ssh.sys_ssh_disable_root_login(c)
        c = c.reconnect(new_port=ssh_port, new_user=admin_user)

        # Verify the new admin user connection and sudo access
        c.run("uname -a", echo=True)
        c.run("id", echo=True)

        # Test sudo access by providing the password
        admin_pass = cfg.get_variable("common", "admin-pass")
        if admin_pass:
            result = c.run(f"echo '{admin_pass}' | sudo -S whoami", echo=True, warn=True)
            if result.return_code == 0:
                print(
                    f"✅ Successfully connected as {admin_user} with SSH key authentication "
                    f"and sudo access"
                )
            else:
                print(f"⚠️  Connected as {admin_user} with SSH keys, but sudo test failed")
        else:
            print(
                f"✅ Successfully connected as {admin_user} with SSH key authentication "
                f"(sudo not tested - no password available)"
            )

    return c
