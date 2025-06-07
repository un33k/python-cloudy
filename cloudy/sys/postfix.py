from fabric import task
from cloudy.util.context import Context
from cloudy.sys.core import sys_restart_service
from cloudy.sys.etc import sys_etc_git_commit

@task
@Context.wrap_context
def sys_install_postfix(c: Context) -> None:
    """ Install postfix for outgoing email (loopback) - Ex: (cmd)"""
    
    # Method 1: Try fixing debconf permissions and using debconf-set-selections
    try:
        c.sudo('chmod 644 /var/cache/debconf/config.dat || true')
        c.sudo('chmod 600 /var/cache/debconf/passwords.dat || true')
        c.sudo('chown root:root /var/cache/debconf/*.dat || true')
        
        # Ensure debconf-utils is installed
        c.sudo('apt update && apt -y install debconf-utils')
        
        # Set debconf selections
        c.sudo('echo "postfix postfix/main_mailer_type select Internet Site" | debconf-set-selections')
        c.sudo('echo "postfix postfix/mailname string localhost" | debconf-set-selections')
        c.sudo('echo "postfix postfix/destinations string localhost.localdomain, localhost" | debconf-set-selections')
        
        # Install postfix
        c.sudo('apt -y install postfix')
        
    except Exception:
        # Method 2: Fallback to non-interactive installation
        print("Debconf method failed, using non-interactive installation...")
        c.sudo('DEBIAN_FRONTEND=noninteractive apt -y install postfix')
    
    # Configure postfix after installation
    c.sudo('/usr/sbin/postconf -e "inet_interfaces = loopback-only"')
    c.sudo('/usr/sbin/postconf -e "mydestination = localhost.localdomain, localhost"')
    c.sudo('/usr/sbin/postconf -e "myhostname = localhost"')
    
    sys_etc_git_commit(c, 'Installed postfix on loopback for outgoing mail')
    sys_restart_service(c, 'postfix')