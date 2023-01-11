import os
import re
import sys

from fabric.api import run
from fabric.api import task
from fabric.api import sudo
from fabric.api import put
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.contrib import files
from fabric.utils import abort

from cloudy.sys.etc import sys_etc_git_commit

def sys_firewall_install():
    """ Install firewall application - Ex: (cmd)"""
    sudo('apt -y install ufw')
    sys_etc_git_commit('Installed firewall (ufw)')


def sys_firewall_secure_server(ssh_port=22):
    """ Secure the server right away - Ex: (cmd)"""
    sudo('ufw logging on')
    sudo('ufw default deny incoming; ufw default allow outgoing')
    sudo('ufw allow {}'.format(ssh_port))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server is secured down')


def sys_firewall_wide_open():
    """ Open up firewall, the server will be wide open - Ex: (cmd)"""
    sudo('ufw default allow incoming; ufw default allow outgoing')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_disable():
    """ Disable firewall, the server will be wide open - Ex: (cmd)"""
    sudo('ufw disable; sudo ufw status verbose')


def sys_firewall_allow_incoming_http():
    """ Allow http (port 80) requests to this server - Ex: (cmd)"""
    sudo('ufw allow http')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_disallow_incoming_http():
    """ Disallow http (port 80) requests to this server - Ex: (cmd)"""
    sudo('ufw delete allow http')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_allow_incoming_https():
    """ Allow http (port 443) requests to this server - Ex: (cmd)"""
    sudo('ufw allow https')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_disallow_incoming_https():
    """ Disallow http (port 443) requests to this server - Ex: (cmd)"""
    sudo('ufw delete allow https')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_allow_incoming_postgresql():
    """ Allow postgresql (port 5432) requests to this server - Ex: (cmd)"""
    sudo('ufw allow postgresql')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_disallow_incoming_postgresql():
    """ Disallow postgresql (port 5432) requests to this server - Ex: (cmd)"""
    sudo('ufw delete allow postgresql')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_allow_incoming_port(port):
    """ Allow requests on specific port to this server - Ex: (cmd:<port>)"""
    sudo('ufw allow {}'.format(port))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_disallow_incoming_port(port):
    """ Disallow requests to this server on specific port - Ex: (cmd:<port>)"""
    sudo('ufw delete allow {}'.format(port))
    with settings(warn_only=False):
        sudo('ufw delete allow {}/tcp'.format(port))
        sudo('ufw delete allow {}/udp'.format(port))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_allow_incoming_port_proto(port, proto):
    """ Allow requests on specific port to this server - Ex: (cmd:<port>,<proto>)"""
    sudo('ufw allow {}/{}'.format(port, proto))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')


def sys_firewall_disallow_incoming_port_proto(port, proto):
    """ Disallow requests to this server on specific port - Ex: (cmd:<port>,<proto>)"""
    sudo('ufw delete allow {}/{}'.format(port, proto))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')

def sys_firewall_allow_incoming_host_port(host, port):
    """ Allow requests from specific host on specific port to this server - Ex: (cmd:<host>,<port>)"""
    sudo('ufw allow from {} to any port {}'.format(host, port))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')

def sys_firewall_disallow_incoming_host_port(host, port):
    """ Allow requests from specific host on specific port to this server - Ex: (cmd:<host>,<port>)"""
    sudo('ufw delete allow from {} to any port {}'.format(host, port))
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')





