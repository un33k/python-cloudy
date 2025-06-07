from fabric import task
from cloudy.util.context import Context
from cloudy.sys.core import sys_reload_service

@task
@Context.wrap_context
def web_create_data_directory(c: Context, web_dir='/srv/www'):
    """Create a data directory for the web files."""
    c.sudo(f'mkdir -p {web_dir}')


@task
@Context.wrap_context
def web_create_shared_directory(c: Context, shared_dir='/srv/www/shared'):
    """Create a shared directory for the site."""
    c.sudo(f'mkdir -p {shared_dir}')
    c.sudo(f'chown -R :www-data {shared_dir}')
    c.sudo(f'chmod -R g+wrx {shared_dir}')

@task
@Context.wrap_context
def web_create_seekrets_directory(c: Context, seekrets_dir='/srv/www/seekrets'):
    """Create a seekrets directory."""
    c.sudo(f'mkdir -p {seekrets_dir}')
    c.sudo(f'chown -R :www-data {seekrets_dir}')
    c.sudo(f'chmod -R g+wrx {seekrets_dir}')

@task
@Context.wrap_context
def web_create_site_directory(c: Context, domain):
    """Create a site directory structure for a domain."""
    path = f'/srv/www/{domain}'
    c.sudo(f'mkdir -p {path}/{{pri,pub,log,bck}}')
    c.sudo(f'chown -R :www-data {path}')
    c.sudo(f'chmod -R g+w {path}/pub')
    c.sudo(f'chmod -R g+w {path}/log')

@task
@Context.wrap_context
def web_create_virtual_env(c: Context, domain, py_version='3'):
    """Create a virtualenv for a domain."""
    path = f'/srv/www/{domain}/pri'
    with c.cd(path):
        c.sudo(f'python{py_version} -m venv venv')
        c.sudo('chown -R :www-data venv')
        c.sudo('chmod -R g+wrx venv')

@task
@Context.wrap_context
def web_create_site_log_file(c: Context, domain):
    """Create a log file with proper permissions for Django."""
    site_logfile = f'/srv/www/{domain}/log/{domain}.log'
    c.sudo(f'touch {site_logfile}')
    c.sudo(f'chown :www-data {site_logfile}')
    c.sudo(f'chmod g+rw {site_logfile}')

@task
@Context.wrap_context
def web_prepare_site(c: Context, domain, py_version='3'):
    """Create a site directory and everything else for the site on production server."""
    web_create_site_directory(c, domain)
    web_create_virtual_env(c, domain, py_version)
    web_create_site_log_file(c, domain)

@task
@Context.wrap_context
def web_deploy(c: Context, domain):
    """Push changes to a production server."""
    webroot = f'/srv/www/{domain}/pri/venv/webroot'
    with c.cd(webroot):
        with c.prefix(f'source {webroot}/../bin/activate'):
            c.run('git pull')
            c.run('pip install -r env/deploy_reqs.txt')
            c.run('bin/manage.py collectstatic --noinput')
            c.run('bin/manage.py migrate')
            sys_reload_service(c, 'nginx')
            c.sudo(f'supervisorctl restart {domain}')

@task
@Context.wrap_context
def web_run_command(c: Context, domain, command):
    """Run a command from the webroot directory of a domain on a production server."""
    webroot = f'/srv/www/{domain}/pri/venv/webroot'
    with c.cd(webroot):
        with c.prefix(f'source {webroot}/../bin/activate'):
            c.run(command)







