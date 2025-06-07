from fabric import Connection, task
from cloudy.sys import docker
from cloudy.sys import openvpn
from cloudy.sys import firewall
from cloudy.util.conf import CloudyConfig
from cloudy.srv import recipe_generic_server
from cloudy.sys import core

@task
def srv_setup_openvpn(c: Connection, generic=True):
    """
    Setup a VPN server(s) - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig()

    if generic:
        recipe_generic_server.srv_setup_generic_server(c)

    # Install and configure Docker for OpenVPN
    admin_user = cfg.get_variable('common', 'admin-user')
    docker.sys_docker_install(c)
    docker.sys_docker_config(c)
    docker.sys_docker_user_group(c, admin_user)

    domain = cfg.get_variable('VPNSERVER', 'vpn-domain')
    if not domain:
        print("domain is missing from VPNSERVER section")
        return

    passphrase = cfg.get_variable('VPNSERVER', 'passphrase', 'nopass')
    repository = cfg.get_variable('VPNSERVER', 'repo', 'kylemanna/openvpn')
    datadir = cfg.get_variable('VPNSERVER', 'data-dir', '/docker/openvpn')
    core.sys_mkdir(c, datadir)

    # Primary OpenVPN instance
    primary_port = cfg.get_variable('VPNSERVER', 'primary-port', '80')
    primary_proto = cfg.get_variable('VPNSERVER', 'primary-proto', 'udp')
    if primary_port and primary_proto:
        openvpn.sys_openvpn_docker_install(
            c,
            domain=domain,
            port=primary_port,
            proto=primary_proto,
            passphrase=passphrase,
            datadir=datadir,
            repo=repository
        )
        openvpn.sys_openvpn_docker_conf(c, domain, primary_port, primary_proto)
        firewall.fw_allow_incoming_port_proto(c, primary_port, primary_proto)

    # Secondary OpenVPN instance
    secondary_port = cfg.get_variable('VPNSERVER', 'secondary-port', '443')
    secondary_proto = cfg.get_variable('VPNSERVER', 'secondary-proto', 'tcp')
    if secondary_port and secondary_proto:
        openvpn.sys_openvpn_docker_install(
            c,
            domain=domain,
            port=secondary_port,
            proto=secondary_proto,
            passphrase=passphrase,
            datadir=datadir,
            repo=repository
        )
        openvpn.sys_openvpn_docker_conf(c, domain, secondary_port, secondary_proto)
        firewall.fw_allow_incoming_port_proto(c, secondary_port, secondary_proto)
