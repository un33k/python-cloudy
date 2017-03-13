import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import get
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_mkdir
from cloudy.util.common import sys_restart_service


def sys_openvpn_docker_install(domain, port=1194, proto='udp', datadir='/docker/openvpn', repo='kylemanna/openvpn'):
    docker_name = "{proto}{port}{domain}".format(domain=domain, port=port, proto=proto)
    docker_data = '{data}/{domain}'.format(data=datadir, domain=domain)

    sys_mkdir(docker_data)
    cmd = "docker run --rm -v {data}:/etc/openvpn {repo} ovpn_genconfig -u {proto}://{domain}:{port}"
    run(cmd.format(data=docker_data, repo=repo, proto=proto, domain=domain, port=port))

    cmd = "docker run --rm -v {data}:/etc/openvpn -it {repo} ovpn_initpki nopass"
    prompts = {
        'Confirm removal: ': 'yes',
        'Common Name (eg: your user, host, or server name) [Easy-RSA CA]:': docker_name
    }
    with settings(prompts=prompts):
        run(cmd.format(data=docker_data, repo=repo))

    cmd = "docker run -v {data}:/etc/openvpn --name {name} -d -p {port}:1194/{proto} --cap-add=NET_ADMIN {repo}"
    run(cmd.format(data=docker_data, repo=repo, proto=proto, port=port, name=docker_name))

    cmd = "docker update --restart=always {name}".format(name=docker_name)
    run(cmd)


def sys_openvpn_docker_conf(domain, port=1194, proto='udp'):
    """ docker openvpn config - Ex: (cmd:)"""
    docker_name = "{proto}{port}{domain}".format(domain=domain, port=port, proto=proto)

    cfgdir = os.path.join(os.path.dirname( __file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'openvpn/docker-systemd.cfg'))
    remotecfg = '/etc/systemd/system/docker-{name}.service'.format(name=docker_name)
    sudo('rm -rf ' + remotecfg)
    put(localcfg, remotecfg, use_sudo=True)
    files.sed(remotecfg, before='docker_port', after='{port}'.format(port=port), use_sudo=True)
    files.sed(remotecfg, before='docker_proto', after='{proto}'.format(proto=proto), use_sudo=True)
    files.sed(remotecfg, before='docker_domain', after='{domain}'.format(domain=domain), use_sudo=True)
    files.sed(remotecfg, before='docker_image_name', after='{name}'.format(name=docker_name), use_sudo=True)
    sys_etc_git_commit('Configured {name} docker'.format(name=docker_name))
    sudo('systemctl daemon-reload')
    sudo('systemctl enable docker-{name}.service'.format(name=docker_name))
    sudo('systemctl start docker-{name}.service'.format(name=docker_name))


def sys_openvpn_docker_create_client(client_name, domain, datadir='/docker/openvpn', repo='kylemanna/openvpn'):
    """ docker openvpn create client - Ex: (cmd:)"""
    docker_data = '{data}/{domain}'.format(data=datadir, domain=domain)
    cmd = "docker run --rm -v {data}:/etc/openvpn  -it {repo} easyrsa build-client-full {client} nopass"
    run(cmd.format(data=docker_data, repo=repo, client=client_name))

    cmd = "docker run --rm -v {data}:/etc/openvpn {repo} ovpn_getclient {client} > /tmp/{client}.ovpn"
    run(cmd.format(data=docker_data, repo=repo, client=client_name))

    remote_file = "/tmp/{client}.ovpn".format(client=client_name)
    local_file = "./{client}.ovpn".format(client=client_name)
    get(remote_file, local_file)

