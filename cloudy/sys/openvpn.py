import os

from fabric import task

from cloudy.sys.core import sys_mkdir
from cloudy.sys.etc import sys_etc_git_commit
from cloudy.util.context import Context


@task
@Context.wrap_context
def sys_openvpn_docker_install(
    c: Context,
    domain: str,
    port: str = "1194",
    proto: str = "udp",
    passphrase: str = "nopass",
    datadir: str = "/docker/openvpn",
    repo: str = "kylemanna/openvpn",
) -> None:
    """Install and initialize OpenVPN in Docker."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f"{datadir}/{docker_name}"

    sys_mkdir(c, docker_data)
    c.run(
        f"docker run --rm -v {docker_data}:/etc/openvpn {repo} "
        f"ovpn_genconfig -u {proto}://{domain}:{port}"
    )

    if passphrase == "nopass":
        cmd = f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} ovpn_initpki nopass"
    else:
        cmd = f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} ovpn_initpki"

    # Note: Fabric 2+ does not support interactive prompts natively
    # like Fabric 1.x's settings(prompts=...)
    # If you need to handle prompts, consider using pexpect or ensure
    # 'nopass' is used for automation.
    c.run(cmd)

    c.run(
        f"docker run -v {docker_data}:/etc/openvpn --name {docker_name} "
        f"-d -p {port}:1194/{proto} --cap-add=NET_ADMIN {repo}"
    )
    c.run(f"docker update --restart=always {docker_name}")


@task
@Context.wrap_context
def sys_openvpn_docker_conf(
    c: Context, domain: str, port: str = "1194", proto: str = "udp"
) -> None:
    """Configure OpenVPN Docker systemd service."""
    docker_name = f"{proto}-{port}.{domain}"
    cfgdir = os.path.join(os.path.dirname(__file__), "../cfg")
    localcfg = os.path.expanduser(os.path.join(cfgdir, "openvpn/docker-systemd.cfg"))
    remotecfg = f"/etc/systemd/system/docker-{docker_name}.service"
    c.sudo(f"rm -rf {remotecfg}")
    c.put(localcfg, remotecfg)
    # Replace placeholders in the config file
    c.sudo(f"sed -i 's/docker_port/{port}/g' {remotecfg}")
    c.sudo(f"sed -i 's/docker_proto/{proto}/g' {remotecfg}")
    c.sudo(f"sed -i 's/docker_domain/{domain}/g' {remotecfg}")
    c.sudo(f"sed -i 's/docker_image_name/{docker_name}/g' {remotecfg}")
    sys_etc_git_commit(c, f"Configured {docker_name} docker")
    c.sudo("systemctl daemon-reload")
    c.sudo(f"systemctl enable docker-{docker_name}.service")
    c.sudo(f"systemctl start docker-{docker_name}.service")


@task
@Context.wrap_context
def sys_openvpn_docker_create_client(
    c: Context,
    client_name: str,
    domain: str,
    port: int = 1194,
    proto: str = "udp",
    passphrase: str = "nopass",
    datadir: str = "/docker/openvpn",
    repo: str = "kylemanna/openvpn",
) -> None:
    """Create a new OpenVPN client and fetch its config."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f"{datadir}/{docker_name}"

    if passphrase == "nopass":
        cmd = (
            f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} "
            f"easyrsa build-client-full {client_name} nopass"
        )
    else:
        cmd = (
            f"docker run --rm -v {docker_data}:/etc/openvpn -it {repo} "
            f"easyrsa build-client-full {client_name}"
        )

    # See note above about prompts
    c.run(cmd)

    cmd = (
        f"docker run --rm -v {docker_data}:/etc/openvpn {repo} "
        f"ovpn_getclient {client_name} > /tmp/{client_name}.ovpn"
    )
    c.run(cmd)

    remote_file = f"/tmp/{client_name}.ovpn"
    local_file = f"/tmp/{client_name}.ovpn"
    c.get(remote_file, local_file)
    c.run(f"rm {remote_file}")


@task
@Context.wrap_context
def sys_openvpn_docker_revoke_client(
    c: Context,
    client_name: str,
    domain: str,
    port: int = 1194,
    proto: str = "udp",
    passphrase: str = "nopass",
    datadir: str = "/docker/openvpn",
    repo: str = "kylemanna/openvpn",
) -> None:
    """Revoke an OpenVPN client."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f"{datadir}/{docker_name}"

    cmd = f"docker run --rm -it -v {docker_data}:/etc/openvpn {repo} easyrsa revoke {client_name}"
    c.run(cmd)
    cmd = f"docker run --rm -it -v {docker_data}:/etc/openvpn {repo} easyrsa gen-crl"
    c.run(cmd)
    c.run(f"docker restart {docker_name}")


@task
@Context.wrap_context
def sys_openvpn_docker_show_client_list(
    c: Context,
    domain: str,
    port: int = 1194,
    proto: str = "udp",
    datadir: str = "/docker/openvpn",
    repo: str = "kylemanna/openvpn",
) -> None:
    """Show the list of OpenVPN clients."""
    docker_name = f"{proto}-{port}.{domain}"
    docker_data = f"{datadir}/{docker_name}"

    cmd = f"docker run --rm -it -v {docker_data}:/etc/openvpn {repo} ovpn_listclients"
    c.run(cmd)
