"""Recipe for OpenVPN server deployment with Docker containerization."""

from fabric import task

from cloudy.srv import recipe_generic_server
from cloudy.sys import core, docker, firewall, openvpn
from cloudy.util.conf import CloudyConfig
from cloudy.util.context import Context


@task
@Context.wrap_context
def setup_openvpn(c: Context, cfg_paths=None, generic=True):
    """
    Setup OpenVPN server with Docker containerization.

    Installs Docker and deploys OpenVPN server in containers with dual-protocol
    support (UDP and TCP), certificate management, and firewall configuration
    for secure VPN access.

    Args:
        cfg_paths: Comma-separated config file paths
        generic: Whether to run generic server setup first

    Example:
        fab recipe.vpn-install --cfg-paths="./.cloudy.generic,./.cloudy.vpn"
    """
    cfg = CloudyConfig(cfg_paths)

    if generic:
        c = recipe_generic_server.setup_server(c, cfg_paths)

    # Install and configure Docker for OpenVPN
    admin_user = cfg.get_variable("common", "admin-user")
    docker.sys_docker_install(c)
    docker.sys_docker_config(c)
    docker.sys_docker_user_group(c, admin_user)

    domain = cfg.get_variable("VPNSERVER", "vpn-domain")
    if not domain:
        print("domain is missing from VPNSERVER section")
        return

    passphrase = cfg.get_variable("VPNSERVER", "passphrase", "nopass")
    repository = cfg.get_variable("VPNSERVER", "repo", "kylemanna/openvpn")
    datadir = cfg.get_variable("VPNSERVER", "data-dir", "/docker/openvpn")
    core.sys_mkdir(c, datadir)

    # Primary OpenVPN instance
    primary_port = cfg.get_variable("VPNSERVER", "primary-port", "80")
    primary_proto = cfg.get_variable("VPNSERVER", "primary-proto", "udp")
    if primary_port and primary_proto:
        openvpn.sys_openvpn_docker_install(
            c,
            domain=domain,
            port=primary_port,
            proto=primary_proto,
            passphrase=passphrase,
            datadir=datadir,
            repo=repository,
        )
        openvpn.sys_openvpn_docker_conf(c, domain, primary_port, primary_proto)
        firewall.fw_allow_incoming_port_proto(c, primary_port, primary_proto)

    # Secondary OpenVPN instance
    secondary_port = cfg.get_variable("VPNSERVER", "secondary-port", "443")
    secondary_proto = cfg.get_variable("VPNSERVER", "secondary-proto", "tcp")
    if secondary_port and secondary_proto:
        openvpn.sys_openvpn_docker_install(
            c,
            domain=domain,
            port=secondary_port,
            proto=secondary_proto,
            passphrase=passphrase,
            datadir=datadir,
            repo=repository,
        )
        openvpn.sys_openvpn_docker_conf(c, domain, secondary_port, secondary_proto)
        firewall.fw_allow_incoming_port_proto(c, secondary_port, secondary_proto)

    # Success message
    print(f"\n🎉 ✅ OPENVPN SERVER SETUP COMPLETED SUCCESSFULLY!")
    print(f"📋 Configuration Summary:")
    print(f"   └── Domain: {domain}")
    print(f"   └── Data Directory: {datadir}")
    print(f"   └── Docker Repository: {repository}")
    print(f"   └── Admin User: {admin_user} (added to docker group)")
    if primary_port and primary_proto:
        print(f"   └── Primary VPN: {primary_port}/{primary_proto.upper()}")
    if secondary_port and secondary_proto:
        print(f"   └── Secondary VPN: {secondary_port}/{secondary_proto.upper()}")
    print(f"   └── Passphrase: {'Configured' if passphrase != 'nopass' else 'Default (nopass)'}")
    print(f"\n🚀 OpenVPN server is ready! Generate client certificates to connect.")
    if generic:
        admin_user = cfg.get_variable("common", "admin-user", "admin")
        ssh_port = cfg.get_variable("common", "ssh-port", "22")
        print(f"   └── Admin SSH: {admin_user}@server:{ssh_port}")
    print(f"\n📝 Next steps: Use OpenVPN container commands to generate client configs")
