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

from cloudy.sys.etc import sys_etc_git_commit

def sys_firewall_install():
    """ Install filrewall application - Ex: (cmd)"""
    sudo('apt-get -y install ufw')
    sys_etc_git_commit('Installed firewall (ufw)')


def sys_firewall_secure_server():
    """ Secure the server right away - Ex: (cmd)"""
    sudo('ufw logging on')
    sudo('ufw default deny incoming; ufw default allow outgoing')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server is secured down')


def sys_firewall_wideopen():
    """ Open up firewall, the server will be wide open - Ex: (cmd)"""
    sudo('ufw default allow incoming; ufw default allow outgoing')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server is wide open')
    

def sys_firewall_disable():
    """ Disable firewall, the server will be wide open - Ex: (cmd)"""
    sudo('ufw disable; sudo ufw status verbose')
    sys_etc_git_commit('Server is disabled - No firewall')


def sys_firwall_allow_incoming_http():
    """ Allow http (port 80) requests to this server - Ex: (cmd)"""
    sudo('ufw allow http')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server now accepts http request on port (80)')


def sys_firwall_disallow_incoming_http():
    """ Disallow http (port 80) requests to this server - Ex: (cmd)"""
    sudo('ufw delete allow http')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server no longer accepts http request on port (80)')


def sys_firwall_allow_incoming_https():
    """ Allow http (port 443) requests to this server - Ex: (cmd)"""
    sudo('ufw allow https')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server now accepts https requests on port (443)')


def sys_firwall_disallow_incoming_https():
    """ Disallow http (port 443) requests to this server - Ex: (cmd)"""
    sudo('ufw delete allow https')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server no longer accepts https requests on port (443)')


def sys_firwall_allow_incoming_postgresql():
    """ Allow postgresql (port 5432) requests to this server - Ex: (cmd)"""
    sudo('ufw allow postgresql')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server now accepts postgresql requests on port (5432)')


def sys_firwall_disallow_incoming_postgresql():
    """ Disallow postgresql (port 5432) requests to this server - Ex: (cmd)"""
    sudo('ufw delete allow postgresql')
    sudo('ufw disable; echo "y" | ufw enable; sudo ufw status verbose')
    sys_etc_git_commit('Server no longer accepts postgresql requests on port (5432)')





