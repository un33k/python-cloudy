# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"  # Install with development dependencies
```

### Core Development Commands
- **List all Fabric tasks**: `fab -l`
- **Run tests**: `python test.py`
- **Run linting**: `./lint.sh` (comprehensive code quality checks)
- **Build package**: `python -m build`
- **Install dev dependencies**: `pip install -e ".[dev]"`

### Modern Command Patterns (NEW)

#### System Operations
```bash
# System information and management
fab -H user@host:port system.info
fab -H user@host system.set-hostname --name=webserver01
fab -H user@host system.update
fab -H user@host system.upgrade --safe=true

# Service management
fab -H user@host system.start-service --name=nginx
fab -H user@host system.restart-service --name=postgresql
```

#### Database Operations (PostgreSQL)
```bash
# User management
fab -H user@host psql.create-user --name=john --password=secret123 --database=myapp
fab -H user@host psql.delete-user --name=john
fab -H user@host psql.set-password --name=john --password=newsecret123

# Database management
fab -H user@host psql.create-database --name=myapp --owner=john
fab -H user@host psql.delete-database --name=myapp
fab -H user@host psql.list-users
fab -H user@host psql.list-databases

# Operations
fab -H user@host psql.backup --database=myapp --destination=/backups
fab -H user@host psql.grant --user=john --database=myapp
fab -H user@host psql.install --version=15
```

#### User Management
```bash
# Create and manage users
fab -H user@host user.create --name=john --groups=docker,www-data --sudo=true
fab -H user@host user.delete --name=john
fab -H user@host user.set-password --name=john --password=newsecret123

# Group management
fab -H user@host user.add-to-group --name=john --group=docker
fab -H user@host user.grant-sudo --name=john
fab -H user@host user.revoke-sudo --name=john
```

#### Modern Recipe System
```bash
# Quick server setups
fab -H user@host recipe.web --config=django --ssl=true --domain=myapp.com
fab -H user@host recipe.database --type=postgresql --gis=true
fab -H user@host recipe.cache --type=redis
fab -H user@host recipe.loadbalancer --type=nginx --ssl=true

# Complete stack deployment
fab -H user@host recipe.full-stack --config=django-postgres-redis

# Quick shortcuts
fab -H user@host recipe.django --domain=myapp.com
fab -H user@host recipe.postgres --gis=true
fab -H user@host recipe.nginx-lb --ssl=true
```

### Command Structure Philosophy

#### New Intuitive Design
- **Module.Action Pattern**: `psql.create-user`, `system.set-hostname`, `user.grant-sudo`
- **Descriptive Names**: Actions use clear verbs (create, delete, set, grant, etc.)
- **Named Parameters**: All parameters use descriptive names (`--name=john` vs positional args)
- **Logical Grouping**: Related commands grouped under intuitive namespaces

#### Benefits of New Structure
1. **Self-Documenting**: Command names clearly indicate what they do
2. **Predictable**: Consistent patterns across all modules
3. **Discoverable**: Easy to explore with `fab -l | grep module`
4. **IDE-Friendly**: Clear parameter names for better autocompletion

### Legacy Command Patterns (DEPRECATED)
```bash
# Old verbose patterns (still work but deprecated)
fab -H user@host:port core.sys-uname
fab recipe-generic-server.setup-server --cfg-file=./.cloudy.generic
fab -H root@host recipe-webserver-django.setup-web --cfg-file=./base.cfg,./web.cfg
```

## Architecture Overview

### Module Structure
- **`cloudy/sys/`** - Low-level system operations (core, docker, ssh, firewall, security, etc.)
- **`cloudy/db/`** - Database automation (PostgreSQL, MySQL, PgBouncer, PgPool, PostGIS)
- **`cloudy/web/`** - Web server automation (Apache, Nginx, Supervisor, GeoIP)
- **`cloudy/srv/`** - High-level deployment recipes that orchestrate other modules
- **`cloudy/util/`** - Configuration management and enhanced Fabric context
- **`cloudy/aws/`** - AWS-specific automation (EC2)

### Configuration System
The configuration system uses INI-style files with **hierarchical precedence** (lowest to highest):
1. `cloudy/cfg/defaults.cfg` - Built-in defaults
2. `~/.cloudy` - User home directory config
3. `./.cloudy` - Current working directory config
4. Explicitly passed files via `--cfg-file`

### Configuration File Structure
```ini
[COMMON]
git-user-full-name = John Doe
git-user-email = john@example.com
timezone = America/New_York
admin-user = admin
hostname = my-server
python-version = 3.8

[WEBSERVER]
webserver = gunicorn
webserver-port = 8181
domain-name = example.com

[DBSERVER]
pg-version = 17
db-host = localhost
db-port = 5432
```

### Recipe Pattern
Recipes are high-level deployment patterns that:
- Use `@task` and `@Context.wrap_context` decorators
- Accept comma-separated `cfg_file` parameters
- Orchestrate multiple system modules
- Follow the pattern: `CloudyConfig(cfg_file.split(','))` → `cfg.get_variable(section, key)`

Example recipe structure:
```python
@task
@Context.wrap_context
def setup_server(c: Context, cfg_file=None):
    cfg = CloudyConfig(cfg_file.split(',') if cfg_file else None)
    hostname = cfg.get_variable('common', 'hostname')
    # Use cfg values to call sys/* modules
```

## Modern Project Configuration

This project uses **pyproject.toml** for modern Python packaging and development tool configuration:

### Project Build System
- **Build backend**: `setuptools` with modern pyproject.toml configuration
- **Package data**: Automatically includes `cloudy/cfg/**/*` configuration files
- **Entry points**: Defines `cloudy` console script

### Development Tools Configuration
All development tools are configured in `pyproject.toml`:
- **Black**: 100-character line length, Python 3.8+ targets
- **isort**: Black-compatible profile with 100-character line length
- **MyPy**: Type checking with Fabric-specific overrides
- **Coverage**: Source analysis for `cloudy` package

### Flake8 Configuration
Located in `.flake8` (since flake8 doesn't support pyproject.toml yet):
- **Line length**: 100 characters
- **Ignored rules**: E203, W503 (Black compatibility)
- **Per-file ignores**: F401 for `__init__.py` files

### License
This project is licensed under the **MIT License** - modern, permissive open source license.

## Development Requirements

- **Python**: ≥3.8
- **Key Dependencies**:
  - Fabric ≥3.2.2 (SSH automation)
  - apache-libcloud ≥3.8.0 (cloud provider abstraction)
  - colorama ≥0.4.6 (colored terminal output)
  - s3cmd ≥2.4.0 (S3 management)
- **Development Dependencies** (install with `pip install -e ".[dev]"`):
  - black ≥23.0.0 (code formatting)
  - isort ≥5.12.0 (import sorting)
  - flake8 ≥6.0.0 (style checking)
  - mypy ≥1.0.0 (type checking)
  - ipython ≥8.7.0 (enhanced REPL)

## Working with Configurations

### Configuration Variables
- Use dash-separated naming: `git-user-full-name`, `ssh-port`, `python-version`
- Section names: `COMMON`, `WEBSERVER`, `DBSERVER`, `CACHESERVER`
- Access via: `cfg.get_variable('section', 'variable', fallback='')`

### Multiple Configuration Files
Multiple configs can be combined with comma separation:
```bash
fab recipe-generic-server.setup-server --cfg-file=./.cloudy.generic,./.cloudy.admin
```

## Code Patterns

### Context Wrapper
All tasks use the enhanced Context wrapper from `cloudy.util.context`:
- Provides colored command output
- Handles SSH reconnection after port changes
- Required decorator: `@Context.wrap_context`

### Fabric Task Definition
```python
from fabric import task
from cloudy.util.context import Context
from cloudy.util.conf import CloudyConfig

@task
@Context.wrap_context
def my_task(c: Context, cfg_file=None):
    cfg = CloudyConfig(cfg_file.split(',') if cfg_file else None)
    # Task implementation
```

### Module Import Patterns
```python
from cloudy.sys import core, python, firewall, user
from cloudy.web import apache, supervisor, nginx
from cloudy.db import psql, pgis, mysql
from cloudy.srv import recipe_generic_server
from cloudy import recipes  # New intuitive recipe system
```

## New Task Development Guidelines

### Creating Intuitive Task Names
When adding new tasks, follow these patterns:

1. **Use action verbs**: `create`, `delete`, `set`, `get`, `list`, `install`, `backup`, `restore`
2. **Use descriptive names**: `set-hostname` not `hostname-configure`
3. **Group logically**: Put all user operations in `user.*`, all PostgreSQL operations in `psql.*`
4. **Add helpful docstrings**: Include Args section and Example usage

### Example New Task
```python
@task(name='create-user')
@Context.wrap_context
def create_user(c: Context, name: str, password: str, database: str = None) -> None:
    \"\"\"Create a PostgreSQL user.
    
    Args:
        name: Username to create
        password: Password for the user
        database: Optional database to grant access to
    
    Example:
        fab -H myserver.com psql.create-user --name=john --password=secret123 --database=myapp
    \"\"\"
    # Implementation using existing functions
    db_psql_create_user(c, name, password)
    if database:
        db_psql_grant_database_privileges(c, database, name)
```

### Task Organization
- **Legacy functions**: Keep original functions for backward compatibility
- **New aliases**: Add intuitive aliases that call legacy functions
- **Clear separation**: Use comments to separate legacy from new sections
- **Documentation**: Always include comprehensive docstrings with examples