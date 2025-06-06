import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo, settings
from fabric.api import put
from fabric.api import env
from fabric.api import hide
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit

def _reload_ufw():
    """Helper to reload and show UFW status."""
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')

def sys_firewall_install():
    """Install UFW firewall."""
    sudo('apt -y install ufw')
    sys_etc_git_commit('Installed firewall (ufw)')


def sys_firewall_secure_server(ssh_port=22):
    """Secure the server: deny all incoming, allow outgoing, allow SSH."""
    sudo('ufw logging on')
    sudo('ufw default deny incoming')
    sudo('ufw default allow outgoing')
    sudo(f'ufw allow {ssh_port}')
    _reload_ufw()
    sys_etc_git_commit('Server is secured down')


def sys_firewall_wide_open():
    """Open up firewall: allow all incoming and outgoing."""
    sudo('ufw default allow incoming')
    sudo('ufw default allow outgoing')
    _reload_ufw()


def sys_firewall_disable():
    """Disable firewall."""
    sudo('ufw disable; sudo ufw status verbose')


def sys_firewall_allow_incoming_http():
    """Allow HTTP (port 80) requests."""
    sudo('ufw allow http')
    _reload_ufw()


def sys_firewall_disallow_incoming_http():
    """Disallow HTTP (port 80) requests."""
    sudo('ufw delete allow http')
    _reload_ufw()


def sys_firewall_allow_incoming_https():
    """Allow HTTPS (port 443) requests."""
    sudo('ufw allow https')
    _reload_ufw()


def sys_firewall_disallow_incoming_https():
    """Disallow HTTPS (port 443) requests."""
    sudo('ufw delete allow https')
    _reload_ufw()


def sys_firewall_allow_incoming_postgresql():
    """Allow PostgreSQL (port 5432) requests."""
    sudo('ufw allow postgresql')
    _reload_ufw()


def sys_firewall_disallow_incoming_postgresql():
    """Disallow PostgreSQL (port 5432) requests."""
    sudo('ufw delete allow postgresql')
    _reload_ufw()


def sys_firewall_allow_incoming_port(port):
    """Allow requests on a specific port."""
    sudo(f'ufw allow {port}')
    _reload_ufw()


def sys_firewall_disallow_incoming_port(port):
    """Disallow requests on a specific port."""
    sudo(f'ufw delete allow {port}')
    with settings(warn_only=False):
        sudo(f'ufw delete allow {port}/tcp')
        sudo(f'ufw delete allow {port}/udp')
    _reload_ufw()


def sys_firewall_allow_incoming_port_proto(port, proto):
    """Allow requests on a specific port/protocol."""
    sudo(f'ufw allow {port}/{proto}')
    _reload_ufw()


def sys_firewall_disallow_incoming_port_proto(port, proto):
    """Disallow requests on a specific port/protocol."""
    sudo(f'ufw delete allow {port}/{proto}')
    _reload_ufw()


def sys_firewall_allow_incoming_host_port(host, port):
    """Allow requests from a specific host on a specific port."""
    sudo(f'ufw allow from {host} to any port {port}')
    _reload_ufw()


def sys_firewall_disallow_incoming_host_port(host, port):
    """Disallow requests from a specific host on a specific port."""
    sudo(f'ufw delete allow from {host} to any port {port}')
    _reload_ufw()





