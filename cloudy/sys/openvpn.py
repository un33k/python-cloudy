import os
from fabric.api import run, sudo, put, get, settings
from fabric.contrib import files
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.sys.core import sys_mkdir
from cloudy.util.common import sys_restart_service


def sys_openvpn_docker_install(domain, port=1194, proto='udp', passphrase='nopass', datadir='/docker/openvpn', repo='kylemanna/openvpn'):
    """Install and initialize OpenVPN in Docker."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f'{datadir}/{docker_name}'

    sys_mkdir(docker_data)
    run(f"docker run --rm -v {docker_data}:/etc/openvpn {repo} ovpn_genconfig -u {proto}://{domain}:{port}")

    if passphrase == 'nopass':
        cmd = f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} ovpn_initpki nopass"
    else:
        cmd = f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} ovpn_initpki"

    prompts = {
        'Confirm removal: ': 'yes',
        'Common Name (eg: your user, host, or server name) [Easy-RSA CA]:': docker_name,
        'Enter pass phrase for /etc/openvpn/pki/private/ca.key:': passphrase,
        'Enter PEM pass phrase:': passphrase
    }
    with settings(prompts=prompts):
        run(cmd)

    run(f"docker run -v {docker_data}:/etc/openvpn --name {docker_name} -d -p {port}:1194/{proto} --cap-add=NET_ADMIN {repo}")
    run(f"docker update --restart=always {docker_name}")


def sys_openvpn_docker_conf(domain, port=1194, proto='udp'):
    """Configure OpenVPN Docker systemd service."""
    docker_name = f"{proto}-{port}.{domain}"
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'openvpn/docker-systemd.cfg'))
    remotecfg = f'/etc/systemd/system/docker-{docker_name}.service'
    sudo(f'rm -rf {remotecfg}')
    put(localcfg, remotecfg, use_sudo=True)
    files.sed(remotecfg, before='docker_port', after=str(port), use_sudo=True)
    files.sed(remotecfg, before='docker_proto', after=proto, use_sudo=True)
    files.sed(remotecfg, before='docker_domain', after=domain, use_sudo=True)
    files.sed(remotecfg, before='docker_image_name', after=docker_name, use_sudo=True)
    sys_etc_git_commit(f'Configured {docker_name} docker')
    sudo('systemctl daemon-reload')
    sudo(f'systemctl enable docker-{docker_name}.service')
    sudo(f'systemctl start docker-{docker_name}.service')


def sys_openvpn_docker_create_client(client_name, domain, port=1194, proto='udp', passphrase='nopass', datadir='/docker/openvpn', repo='kylemanna/openvpn'):
    """Create a new OpenVPN client and fetch its config."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f'{datadir}/{docker_name}'

    if passphrase == 'nopass':
        cmd = f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} easyrsa build-client-full {client_name} nopass"
    else:
        cmd = f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} easyrsa build-client-full {client_name}"

    prompts = {
        'Enter PEM pass phrase:': passphrase,
        'Enter pass phrase for /etc/openvpn/pki/private/ca.key:': passphrase,
    }
    with settings(prompts=prompts):
        sudo(cmd)

    cmd = f"docker run --rm -v {docker_data}:/etc/openvpn {repo} ovpn_getclient {client_name} > /tmp/{client_name}.ovpn"
    run(cmd)

    remote_file = f"/tmp/{client_name}.ovpn"
    local_file = f"/tmp/{client_name}.ovpn"
    get(remote_file, local_file)
    run(f'rm {remote_file}')


def sys_openvpn_docker_revoke_client(client_name, domain, port=1194, proto='udp', passphrase='nopass', datadir='/docker/openvpn', repo='kylemanna/openvpn'):
    """Revoke an OpenVPN client."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f'{datadir}/{docker_name}'

    cmd = f"docker run --rm -it -v {docker_data}:/etc/openvpn {repo} easyrsa revoke {client_name}"
    prompts = {
        'Continue with revocation: ': 'yes',
        'Enter pass phrase for /etc/openvpn/pki/private/ca.key:': passphrase,
    }
    with settings(prompts=prompts, warn_only=True):
        sudo(cmd)

    cmd = f"docker run --rm -it -v {docker_data}:/etc/openvpn {repo} easyrsa gen-crl"
    with settings(prompts=prompts):
        run(cmd)

    run(f"docker restart {docker_name}")


def sys_openvpn_docker_show_client_list(domain, port=1194, proto='udp', datadir='/docker/openvpn', repo='kylemanna/openvpn'):
    """Show the list of OpenVPN clients."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f'{datadir}/{docker_name}'

    cmd = f"docker run --rm -it -v {docker_data}:/etc/openvpn {repo} ovpn_listclients"
    with settings(warn_only=True):
        sudo(cmd)
