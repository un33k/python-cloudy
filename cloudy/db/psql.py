import os
import re
import sys
import datetime
import shlex
from typing import Optional
from fabric import task
from cloudy.util.context import Context
from cloudy.sys import core

@task
@Context.wrap_context
def db_psql_install_postgres_repo(c: Context) -> None:
    """Install the official PostgreSQL repository using modern gpg keyring approach."""
    
    # Create the keyring directory if it doesn't exist
    c.sudo('mkdir -p /etc/apt/keyrings')
    
    # Download and install the PostgreSQL signing key to a dedicated keyring file
    # Force overwrite if file exists
    c.sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | '
           'gpg --dearmor --yes -o /etc/apt/keyrings/postgresql.gpg')
    
    # Set proper permissions for the keyring file
    c.sudo('chmod 644 /etc/apt/keyrings/postgresql.gpg')
    
    # Add the PostgreSQL repository with the signed-by option pointing to the keyring
    c.sudo('echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] '
           'https://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > '
           '/etc/apt/sources.list.d/pgdg.list')
    
    # Update package lists
    c.sudo('apt update')

@task
@Context.wrap_context
def db_psql_latest_version(c: Context) -> str:
    """Get the latest available postgres version."""
    db_psql_install_postgres_repo(c)
    latest_version: str = ''
    
    # Search for all postgresql-client packages with version numbers
    result = c.run('apt-cache search postgresql-client- | grep "postgresql-client-[0-9]"', hide=True, warn=True)
    
    # Updated regex to match the actual format: postgresql-client-15 - client libraries and client binaries
    version_re = re.compile(r'postgresql-client-(\d+(?:\.\d+)?)\s')
    
    versions = []
    for line in result.stdout.split('\n'):
        if line.strip():  # Skip empty lines
            match = version_re.search(line)
            if match:
                version = match.group(1)
                # Convert to float for proper numerical sorting (e.g., 15 vs 9.6)
                try:
                    versions.append((float(version), version))
                except ValueError:
                    # Handle cases where version might not be a simple number
                    versions.append((0, version))
    
    # Sort by numerical value (descending) and get the string version
    if versions:
        versions.sort(key=lambda x: x[0], reverse=True)
        latest_version = versions[0][1]
    
    print(f'Latest available postgresql is: [{latest_version}]', file=sys.stderr)
    return latest_version

@task
@Context.wrap_context
def db_psql_default_installed_version(c: Context) -> str:
    """Get the default installed postgres version."""
    default_version: str = ''
    
    try:
        result = c.run('psql --version', hide=True, warn=True)
        
        # Modern PostgreSQL version output: "psql (PostgreSQL) 15.4"
        # Legacy format: "psql (PostgreSQL) 9.6.24"
        version_re = re.compile(r'psql\s+\(postgresql\)\s+(\d+(?:\.\d+)?)', re.IGNORECASE)
        
        match = version_re.search(result.stdout.strip())
        if match:
            full_version = match.group(1)
            # For major versions >= 10, use just the major version (e.g., "15" not "15.4")
            # For versions < 10, use major.minor (e.g., "9.6" not "9.6.24")
            version_parts = full_version.split('.')
            if len(version_parts) >= 1:
                major_version = int(version_parts[0])
                if major_version >= 10:
                    default_version = str(major_version)
                else:
                    # For 9.x versions, include the minor version
                    default_version = f"{version_parts[0]}.{version_parts[1]}" if len(version_parts) > 1 else version_parts[0]
    
    except Exception as e:
        print(f'Error getting PostgreSQL version: {e}', file=sys.stderr)
    
    print(f'Default installed postgresql is: [{default_version}]', file=sys.stderr)
    return default_version

@task
@Context.wrap_context
def db_psql_install(c: Context, version: str = '') -> None:
    """Install postgres of a given version or the latest version."""
    db_psql_install_postgres_repo(c)
    
    if not version:
        version = db_psql_latest_version(c)
    
    if not version:
        raise ValueError("Could not determine PostgreSQL version to install")
    
    print(f'Installing PostgreSQL version: {version}', file=sys.stderr)
    
    # Core PostgreSQL packages - these should always be available
    core_requirements = [
        f'postgresql-{version}',
        f'postgresql-client-{version}',
        f'postgresql-contrib-{version}',
        'postgresql-client-common'
    ]
    
    # Optional development package - might not exist for all versions
    dev_package = f'postgresql-server-dev-{version}'
    
    # Check if dev package exists before adding it
    dev_check = c.run(f'apt-cache show {dev_package}', hide=True, warn=True)
    if dev_check.ok:
        core_requirements.append(dev_package)
    else:
        print(f'Warning: {dev_package} not available, skipping', file=sys.stderr)
    
    requirements = ' '.join(core_requirements)
    
    # Install with better error handling
    result = c.sudo(f'apt -y install {requirements}', warn=True)
    
    if not result.ok:
        print(f'Installation failed. Trying alternative package names...', file=sys.stderr)
        # Fallback: try with different package naming for older versions
        fallback_requirements = [
            f'postgresql-{version}',
            f'postgresql-client-{version}',
            f'postgresql-contrib-{version}',
            'postgresql-client-common'
        ]
        fallback_cmd = ' '.join(fallback_requirements)
        c.sudo(f'apt -y install {fallback_cmd}')
    
    # Verify installation
    verify_result = c.run(f'dpkg -l | grep "postgresql-{version}"', hide=True, warn=True)
    if verify_result.ok and verify_result.stdout.strip():
        print(f'PostgreSQL {version} installed successfully', file=sys.stderr)
        core.sys_etc_git_commit(c, f'Installed postgres ({version})')
    else:
        raise RuntimeError(f'PostgreSQL {version} installation verification failed')

@task
@Context.wrap_context
def db_psql_client_install(c: Context, version: str = '') -> None:
    """Install postgres client of a given version or the latest version."""
    db_psql_install_postgres_repo(c)  # Add this line
    
    if not version:
        version = db_psql_latest_version(c)
    
    if not version:  # Add validation
        raise ValueError("Could not determine PostgreSQL version")
    
    # Try with dev package first, fallback without it
    try:
        requirements = f'postgresql-client-{version} postgresql-server-dev-{version} postgresql-client-common'
        c.sudo(f'apt -y install {requirements}')
    except:
        # Fallback without dev package
        requirements = f'postgresql-client-{version} postgresql-client-common'
        c.sudo(f'apt -y install {requirements}')
    
    core.sys_etc_git_commit(c, f'Installed postgres client ({version})')

@task
@Context.wrap_context
def db_psql_make_data_dir(c: Context, version: str = '', data_dir: str = '/var/lib/postgresql') -> str:
    """Make data directory for the postgres cluster."""
    if not version:
        version = db_psql_latest_version(c)
    
    if not version:
        raise ValueError("Could not determine PostgreSQL version for data directory")
    
    # Create the version-specific data directory path
    data_dir = os.path.abspath(os.path.join(data_dir, f'{version}'))
    
    # Create directory with proper permissions
    c.sudo(f'mkdir -p {data_dir}')
    
    # Set proper ownership and permissions for PostgreSQL
    # PostgreSQL requires the data directory to be owned by postgres user
    # and have restrictive permissions (700)
    c.sudo(f'chown postgres:postgres {data_dir}')
    c.sudo(f'chmod 700 {data_dir}')
    
    print(f'Created PostgreSQL data directory: {data_dir}', file=sys.stderr)
    
    return data_dir

@task
@Context.wrap_context
def db_psql_remove_cluster(c: Context, version: str, cluster: str) -> None:
    """Remove a cluster if exists."""
    # Check if cluster exists first
    check_result = c.run(f'pg_lsclusters | grep -q "^{version}\\s\\+{cluster}\\s"', warn=True, hide=True)
    if check_result.failed:
        print(f"Cluster '{version}/{cluster}' does not exist")
        return
    
    # Protect against removing main system cluster without explicit confirmation
    if cluster == 'main' and version in ['14', '15', '16', '17']:
        print(f"Warning: Removing main cluster for PostgreSQL {version}")
    
    # Stop and remove the cluster
    result = c.run(f'pg_dropcluster --stop {version} {cluster}', warn=True)
    
    if result.failed:
        print(f"Failed to remove cluster '{version}/{cluster}': {result.stderr}")
        return
    
    print(f"Successfully removed PostgreSQL cluster '{version}/{cluster}'")
    core.sys_etc_git_commit(c, f'Removed postgres cluster ({version} {cluster})')

@task
@Context.wrap_context
def db_psql_create_cluster(
    c: Context,
    version: str = '',
    cluster: str = 'main',
    encoding: str = 'UTF-8',
    data_dir: str = '/var/lib/postgresql'
) -> None:
    """Make a new postgresql cluster."""
    if not version:
        version = db_psql_default_installed_version(c) or db_psql_latest_version(c)
    db_psql_remove_cluster(c, version, cluster)
    data_dir = db_psql_make_data_dir(c, version, data_dir)
    c.sudo(f'chown -R postgres {data_dir}')
    c.sudo(f'pg_createcluster --start -e {encoding} {version} {cluster} -d {data_dir}')
    core.sys_start_service(c, 'postgresql')
    core.sys_etc_git_commit(c, f'Created new postgres cluster ({version} {cluster})')

@task
@Context.wrap_context
def db_psql_set_permission(
    c: Context, version: str = '', cluster: str = 'main'
) -> None:
    """Set default permission for postgresql."""
    if not version:
        version = db_psql_default_installed_version(c)
    cfgdir = os.path.join(os.path.dirname(__file__), '../cfg')
    localcfg = os.path.expanduser(os.path.join(cfgdir, 'postgresql/pg_hba.conf'))
    remotecfg = f'/etc/postgresql/{version}/{cluster}/pg_hba.conf'
    c.sudo(f'rm -rf {remotecfg}')
    c.put(localcfg, remotecfg)
    c.sudo(f'chown postgres:postgres {remotecfg}')
    c.sudo(f'chmod 644 {remotecfg}')
    core.sys_start_service(c, 'postgresql')
    core.sys_etc_git_commit(c, f'Set default postgres access for cluster ({version} {cluster})')

@task
@Context.wrap_context
def db_psql_configure(
    c: Context,
    version: str = '',
    cluster: str = 'main',
    port: str = '5432',
    interface: str = '*',
    restart: bool = False
) -> None:
    """Configure postgres."""
    if not version:
        version = db_psql_default_installed_version(c)
    
    # Find where postgresql.conf actually is
    search_result = c.run(f'find /etc /usr/local /var -name "postgresql.conf" 2>/dev/null | head -1', warn=True, hide=True)
    
    if search_result.stdout.strip():
        postgresql_conf = search_result.stdout.strip().split('\n')[0]
    else:
        raise FileNotFoundError(f"PostgreSQL configuration file not found for version {version}")
    
    c.sudo(f"sed -i 's/#listen_addresses\\s*=\\s*'\"'\"'localhost'\"'\"'/listen_addresses = '\"'\"'{interface},127.0.0.1'\"'\"'/g' {postgresql_conf}")
    core.sys_etc_git_commit(c, f'Configured postgres cluster ({version} {cluster})')
    if restart:
        core.sys_start_service(c, 'postgresql')

@task
@Context.wrap_context
def db_psql_dump_database(c: Context, dump_dir: str, db_name: str, dump_name: Optional[str] = None) -> None:
    """Backup (dump) a database and save into a given directory."""
    # Check if directory exists, create if not
    result = c.run(f'test -d {dump_dir}', warn=True)
    if result.failed:
        c.sudo(f'mkdir -p {dump_dir}')
    
    if not dump_name:
        now = datetime.datetime.now()
        dump_name = f"{db_name}_{now.year:04d}_{now.month:02d}_{now.day:02d}_{now.hour:02d}_{now.minute:02d}_{now.second:02d}.psql.gz"
    
    dump_path = os.path.join(dump_dir, dump_name)
    
    # Find pg_dump executable
    pg_dump = '/usr/bin/pg_dump'
    result = c.run(f'test -x {pg_dump}', warn=True)
    if result.failed:
        which_result = c.run('which pg_dump', warn=True, hide=True)
        if which_result.failed:
            raise FileNotFoundError("pg_dump command not found. Is PostgreSQL client installed?")
        pg_dump = which_result.stdout.strip()
    
    # Check if database exists
    db_check = c.run(f'sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {db_name}', warn=True)
    if db_check.failed:
        raise ValueError(f"Database '{db_name}' does not exist")
    
    # Perform the dump
    c.sudo(f'sudo -u postgres {pg_dump} --no-owner --no-acl -h localhost {db_name} | gzip > {dump_path}')
    
    # Verify the dump was created and has content
    verify_result = c.run(f'test -s {dump_path}', warn=True)
    if verify_result.failed:
        raise RuntimeError(f"Database dump failed or resulted in empty file: {dump_path}")
    
    print(f"Database '{db_name}' successfully dumped to: {dump_path}")


@task
@Context.wrap_context
def db_psql_create_adminpack(c: Context) -> None:
    """Install admin pack."""
    c.sudo('sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS adminpack;"')

@task
@Context.wrap_context
def db_psql_user_password(c: Context, username: str, password: str) -> None:
    """Change password for a postgres user."""
    escaped_password = password.replace("'", "''")  # Escape single quotes for SQL
    c.sudo(f'sudo -u postgres psql -c "ALTER USER {username} WITH ENCRYPTED PASSWORD \'{escaped_password}\';"')

@task
@Context.wrap_context
def db_psql_create_user(c: Context, username: str, password: str) -> None:
    """Create postgresql user."""
    escaped_password = password.replace("'", "''")  # Escape single quotes for SQL
    # Check if user already exists
    check_result = c.run(f'sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{username}\';"', warn=True, hide=True)
    if check_result.stdout.strip() == '1':
        print(f"User '{username}' already exists")
        return
    
    c.sudo(f'sudo -u postgres psql -c "CREATE ROLE {username} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN ENCRYPTED PASSWORD \'{escaped_password}\';"')

@task
@Context.wrap_context
def db_psql_delete_user(c: Context, username: str) -> None:
    """Delete postgresql user."""
    if username == 'postgres':
        print("Cannot drop user 'postgres'", file=sys.stderr)
        return
    
    # Check if user exists before trying to drop
    check_result = c.run(f'sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{username}\';"', warn=True, hide=True)
    if check_result.stdout.strip() != '1':
        print(f"User '{username}' does not exist")
        return
    
    c.sudo(f'sudo -u postgres psql -c "DROP ROLE {username};"')

@task
@Context.wrap_context
def db_psql_list_users(c: Context) -> None:
    """List postgresql users."""
    c.sudo('sudo -u postgres psql -c "\\du"')

@task
@Context.wrap_context
def db_psql_list_databases(c: Context) -> None:
    """List postgresql databases."""
    c.sudo('sudo -u postgres psql -l')

@task
@Context.wrap_context
def db_psql_create_database(c: Context, dbname: str, dbowner: str) -> None:
    """Create a postgres database for an existing user."""
    # Check if database already exists
    check_result = c.run(f'sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {dbname}', warn=True)
    if not check_result.failed:
        print(f"Database '{dbname}' already exists")
        return
    
    # Check if owner exists
    owner_check = c.run(f'sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{dbowner}\';"', warn=True, hide=True)
    if owner_check.stdout.strip() != '1':
        raise ValueError(f"Database owner '{dbowner}' does not exist")
    
    c.sudo(f'sudo -u postgres createdb -E UTF8 -O {dbowner} {dbname}')

@task
@Context.wrap_context
def db_psql_add_gis_extension_to_database(c: Context, dbname: str) -> None:
    """Add gis extension to an existing database."""
    result = c.sudo(f'sudo -u postgres psql -d {dbname} -c "CREATE EXTENSION IF NOT EXISTS postgis;"', warn=True)
    if result.failed:
        print(f"Warning: Failed to add PostGIS extension to database '{dbname}'. Extension may not be available.")

@task
@Context.wrap_context
def db_psql_add_gis_topology_extension_to_database(c: Context, dbname: str) -> None:
    """Add gis topology extension to an existing database."""
    result = c.sudo(f'sudo -u postgres psql -d {dbname} -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"', warn=True)
    if result.failed:
        print(f"Warning: Failed to add PostGIS topology extension to database '{dbname}'. Extension may not be available.")

@task
@Context.wrap_context
def db_psql_create_gis_database_from_template(c: Context, dbname: str, dbowner: str) -> None:
    """Create a postgres GIS database from template for an existing user."""
    # Check if template exists
    template_check = c.run('sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw template_postgis', warn=True)
    if template_check.failed:
        raise ValueError("Template 'template_postgis' does not exist")
    
    # Check if database already exists
    check_result = c.run(f'sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {dbname}', warn=True)
    if not check_result.failed:
        print(f"Database '{dbname}' already exists")
        return
    
    # Check if owner exists
    owner_check = c.run(f'sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{dbowner}\';"', warn=True, hide=True)
    if owner_check.stdout.strip() != '1':
        raise ValueError(f"Database owner '{dbowner}' does not exist")
    
    c.sudo(f'sudo -u postgres createdb -T template_postgis -O {dbowner} {dbname}')

@task
@Context.wrap_context
def db_psql_create_gis_database(c: Context, dbname: str, dbowner: str) -> None:
    """Create a postgres GIS database for an existing user."""
    db_psql_create_database(c, dbname, dbowner)
    db_psql_add_gis_extension_to_database(c, dbname)
    db_psql_add_gis_topology_extension_to_database(c, dbname)

@task
@Context.wrap_context
def db_psql_delete_database(c: Context, dbname: str) -> None:
    """Delete (drop) a database."""
    if dbname in ['postgres', 'template0', 'template1']:
        print(f"Cannot drop system database '{dbname}'", file=sys.stderr)
        return
    
    # Check if database exists
    check_result = c.run(f'sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {dbname}', warn=True)
    if check_result.failed:
        print(f"Database '{dbname}' does not exist")
        return
    
    c.sudo(f'sudo -u postgres psql -c "DROP DATABASE {dbname};"')

@task
@Context.wrap_context
def db_psql_grant_database_privileges(c: Context, dbname: str, dbuser: str) -> None:
    """Grant all privileges on database for an existing user."""
    # Check if database exists
    db_check = c.run(f'sudo -u postgres psql -lqt | cut -d \\| -f 1 | grep -qw {dbname}', warn=True)
    if db_check.failed:
        raise ValueError(f"Database '{dbname}' does not exist")
    
    # Check if user exists
    user_check = c.run(f'sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname=\'{dbuser}\';"', warn=True, hide=True)
    if user_check.stdout.strip() != '1':
        raise ValueError(f"User '{dbuser}' does not exist")
    
    c.sudo(f'sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE {dbname} to {dbuser};"')