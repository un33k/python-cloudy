import os

from fabric.api import env

from cloudy.db import *
from cloudy.sys import *
from cloudy.web import *
from cloudy.util import *

from cloudy.srv.recipe_generic_server import srv_setup_generic_server
from cloudy.sys.core import sys_mkdir


def srv_setup_vpn(cfg_files, generic=True):
    """
    Setup a vpn server(s) - Ex: (cmd:[cfg-file])
    """
    cfg = CloudyConfig(filenames=cfg_files)

    if generic:
        srv_setup_generic_server(cfg_files)

    #install docker
    admin_user = cfg.get_variable('common', 'admin-user')
    sys_docker_install()
    sys_docker_config()
    sys_docker_user_group(admin_user)

    domain = cfg.get_variable('VPNSERVER', 'vpn-domain')
    if not domain:
        print("domain is missing from VPNSERVER section")
        return

    passphrase = cfg.get_variable('VPNSERVER', 'passphrase', 'nopass')
    repository = cfg.get_variable('VPNSERVER', 'repo', 'kylemanna/openvpn')
    datadir = cfg.get_variable('VPNSERVER', 'data-dir', '/docker/openvpn')
    sys_mkdir(datadir)

    primary_port = cfg.get_variable('VPNSERVER', 'primary-port', '80')
    primary_proto = cfg.get_variable('VPNSERVER', 'primary-proto', 'udp')

    if primary_port and primary_proto:
        sys_openvpn_docker_install(
            domain=domain,
            port=primary_port,
            proto=primary_proto,
            passphrase=passphrase,
            datadir=datadir,
            repo=repository
        )
        sys_openvpn_docker_conf(domain, primary_port, primary_proto)
        sys_firewall_allow_incoming_port_proto(primary_port, primary_proto)


    secondary_port = cfg.get_variable('VPNSERVER', 'secondary-port', '443')
    secondary_proto = cfg.get_variable('VPNSERVER', 'secondary-proto', 'tcp')

    if secondary_port and secondary_port:
        sys_openvpn_docker_install(
            domain=domain,
            port=secondary_port,
            proto=secondary_proto,
            passphrase=passphrase,
            datadir=datadir,
            repo=repository
        )
        sys_openvpn_docker_conf(domain, secondary_port, secondary_proto)
        sys_firewall_allow_incoming_port_proto(secondary_port, secondary_proto)
