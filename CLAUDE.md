# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

**⚠️ CRITICAL**: Always use `.venv` (not `venv`) for the virtual environment!

```bash
# Automated setup (recommended)
./bootstrap.sh

# OR manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Before any Python/Fabric commands, ALWAYS activate:**
```bash
source .venv/bin/activate
```

### Core Development Commands
- **List all Fabric tasks**: `fab -l`
- **Run tests**: `python test.py`
- **Run linting**: `./pep8.sh` (PEP8 compliance checking)
- **Publish package**: `python setup.py publish`

### Fabric Command Patterns

```bash
# High-level server deployment (one command setups)
fab setup.server --cfg-file=./.cloudy.production
fab setup.database --cfg-file=./.cloudy.production
fab setup.web --cfg-file=./.cloudy.production
fab setup.cache
fab setup.load-balancer

# Database operations
fab db.pg.create-user --username=webapp --password=secure123
fab db.pg.create-db --dbname=myapp --dbowner=webapp
fab db.pg.dump --dump-dir=/backups --db-name=myapp
fab db.my.create-user --root-pass=rootpwd --user=webapp --user-pass=secure123

# System administration  
fab system.hostname --hostname=myserver.com
fab system.add-user --username=admin
fab system.ssh-port --port=2222
fab system.timezone --timezone=America/New_York

# Security
fab security.install-firewall
fab security.secure-server --ssh-port=2222
fab security.disable-root

# Services
fab cache.install
fab cache.configure
fab docker.install
fab docker.add-user --username=myuser

# Get help
fab help                    # Show all command categories with examples
```

#### Command Categories
- **setup.***: One-command server deployment recipes
- **system.***: System configuration (hostname, users, SSH, timezone)
- **db.pg.***: PostgreSQL operations (create, backup, users)
- **db.my.***: MySQL operations (create, backup, users)
- **db.pgb.***: PgBouncer connection pooling
- **db.pgp.***: PgPool load balancing  
- **db.gis.***: PostGIS spatial database extensions
- **security.***: Security and firewall configuration
- **cache.***: Redis cache management
- **docker.***: Docker installation and configuration

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

## Development Requirements

- **Python**: ≥3.8
- **Key Dependencies**:
  - Fabric ≥3.2.2 (SSH automation)
  - apache-libcloud ≥3.8.0 (cloud provider abstraction)
  - colorama ≥0.4.6 (colored terminal output)
  - s3cmd ≥2.4.0 (S3 management)

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
from cloudy.sys import core, python, firewall
from cloudy.web import apache, supervisor
from cloudy.db import psql, pgis
from cloudy.srv import recipe_generic_server
```