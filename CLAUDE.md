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
- **Run tests**: `./test.sh` (minimal test suite from `tests/` directory)
- **Run linting**: `./lint.sh` (Black, isort, flake8, mypy)
- **Verbose output**: `CLOUDY_VERBOSE=1 fab [command]` (shows all command output)
- **Debug mode**: `fab --debug [command]` (Fabric debug + all output)
- **Spell checking**: Configured via `.cspell.json` and `.vscode/settings.json`
- **Publish package**: `python setup.py publish`

### Secure Server Management

**⚠️ IMPORTANT**: After running `recipe.gen-install`, root login is disabled for security.

**⚠️ CRITICAL - Sudo Password Requirements**:

Due to underlying issues with Fabric, Python Cloudy does NOT support interactive password prompts. For any sudo operations, you MUST export the password as an environment variable:

```bash
# REQUIRED: Set sudo password via environment variable
export INVOKE_SUDO_PASSWORD=admin_user_password

# Then run commands normally
fab -H admin@server:port command
```

This applies to ALL non-root operations including:
- System administration (`sys.*`)
- Database management (`db.*`)
- Web server operations (`web.*`)
- Service management (`services.*`)
- Firewall configuration (`fw.*`)

**Alternative: Fabric Built-in Password Prompts**:
Fabric provides command-line options for password prompting, though these may not work reliably with Python Cloudy:

```bash
# SSH authentication password prompt
fab --prompt-for-login-password -H user@server command

# Sudo password prompt  
fab --prompt-for-sudo-password -H user@server command
```

**⚠️ WARNING**: These Fabric options may not work consistently due to underlying Fabric issues. The environment variable approach (`INVOKE_SUDO_PASSWORD`) is the recommended and reliable method.

**Complete Secure Workflow Example**:
```bash
# 1. Setup secure server (disables root, creates admin user with SSH keys) 
source .venv/bin/activate
fab -H root@10.10.10.198 recipe.gen-install --cfg-file=./.cloudy.generic

# 2. After setup, connect as admin user with sudo access
export INVOKE_SUDO_PASSWORD=pass4admin
fab -H admin@10.10.10.198:22022 web.nginx.install
fab -H admin@10.10.10.198:22022 db.pg.install
fab -H admin@10.10.10.198:22022 fw.allow-http

# 3. Use verbose/debug flags to control output
CLOUDY_VERBOSE=1 fab -H admin@10.10.10.198:22022 db.pg.status  # Show all output
fab -H admin@10.10.10.198:22022 --debug fw.status             # Show debug info + all output
fab -H admin@10.10.10.198:22022 --echo sys.services           # Echo commands + smart output
fab -H admin@10.10.10.198:22022 sys.services                  # Smart output (hides install noise)
```

**Security Features**:
- ✅ Root login disabled (`PermitRootLogin no`)
- ✅ Admin user with SSH key authentication
- ✅ Custom SSH port (default: 22022)
- ✅ UFW firewall configured
- ✅ Password + sudo access for privileged operations

**Smart Output System**:
- ✅ **Default**: Hides noisy installation commands, shows status/informational commands
- ✅ **CLOUDY_VERBOSE=1**: Shows all command output (environment variable)
- ✅ **--debug/-d**: Shows debug information and all output (Fabric built-in)
- ✅ **--echo/-e**: Echo commands before running (Fabric built-in)
- ✅ **Always Shown**: `ufw status`, `df`, `ps`, `systemctl status`, `pg_lsclusters`, etc.
- ✅ **Hidden by Default**: `apt install`, `wget`, `make`, `pip install`, `pg_createcluster`, `createdb`, etc.

**Recipe Success Messages**:
- ✅ **Comprehensive Summaries**: All recipes show detailed configuration summaries upon completion
- ✅ **Visual Indicators**: 🎉 ✅ success icons and 🚀 ready-to-use messages
- ✅ **Configuration Details**: Ports, addresses, users, versions, firewall rules
- ✅ **Next Steps**: Connection information and usage guidance
- ✅ **Consistent Format**: Standardized success output across all recipe types

### Fabric Command Patterns

```bash
# High-level server deployment (one command setups)
fab recipe.gen-install --cfg-file=./.cloudy.production
fab recipe.psql-install --cfg-file=./.cloudy.production
fab recipe.web-install --cfg-file=./.cloudy.production
fab recipe.redis-install --cfg-file=./.cloudy.production
fab recipe.lb-install --cfg-file=./.cloudy.production

# Database operations
fab db.pg.create-user --username=webapp --password=secure123
fab db.pg.create-db --database=myapp --owner=webapp
fab db.pg.dump --database=myapp
fab db.my.create-user --username=webapp --password=secure123

# System administration  
fab sys.hostname --hostname=myserver.com
fab sys.add-user --username=admin
fab sys.ssh-port --port=2222
fab sys.timezone --timezone=America/New_York

# Security & Firewall
fab fw.install
fab fw.secure-server --ssh-port=2222
fab fw.allow-http
fab fw.allow-https
fab security.install-common

# Services
fab services.cache.install
fab services.cache.configure
fab services.docker.install
fab services.docker.add-user --username=myuser

# Get help
fab help                    # Show all command categories with examples
```

#### Command Categories
- **recipe.***: One-command server deployment recipes (7 commands)
- **sys.***: System configuration (hostname, users, SSH, timezone) (31 commands)
- **db.pg.***: PostgreSQL operations (create, backup, users) (17 commands)
- **db.my.***: MySQL operations (create, backup, users) (7 commands)
- **db.pgb.***: PgBouncer connection pooling (3 commands)
- **db.pgp.***: PgPool load balancing (2 commands)
- **db.gis.***: PostGIS spatial database extensions (4 commands)
- **fw.***: Firewall configuration (9 commands)
- **security.***: Security hardening (1 command)
- **services.***: Service management (Docker, Redis, Memcached, VPN) (17 commands)
- **web.***: Web server management (Apache, Nginx, Supervisor) (13 commands)
- **aws.***: Cloud management (EC2) (16 commands)

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
python-version = 3.11

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
- **Key Dependencies** (defined in `pyproject.toml` and `requirements.txt`):
  - Fabric ≥3.2.2 (SSH automation)
  - apache-libcloud ≥3.8.0 (cloud provider abstraction)
  - colorama ≥0.4.6 (colored terminal output)
  - s3cmd ≥2.4.0 (S3 management)
  - Development tools: Black, isort, flake8, mypy

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