# Python Cloudy

**Infrastructure automation toolkit for cloud and server management**

---

## Overview

Python Cloudy is a comprehensive infrastructure automation toolkit that simplifies server configuration, database management, web server setup, and cloud deployments. Built on top of Fabric, it provides over 120 organized commands for system administration and DevOps workflows.

### Key Features

- 🚀 **High-level deployment recipes** for complete server setups
- 🗄️ **Database automation** (PostgreSQL, MySQL, Redis, Memcached)
- 🌐 **Web server management** (Apache, Nginx, Supervisor)
- ☁️ **Cloud integration** (AWS EC2)
- 🔒 **Security & firewall** configuration
- 🔧 **System administration** utilities

---

## Quick Start

### Automated Setup (Recommended)
```bash
git clone https://github.com/un33k/python-cloudy
cd python-cloudy
./bootstrap.sh
```

### Manual Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Verify Installation
```bash
source .venv/bin/activate
fab -l
```

---

## Important: Sudo Password Configuration

**⚠️ CRITICAL**: Due to underlying issues with Fabric, Python Cloudy requires explicit sudo password configuration since interactive password prompts are not supported in automated deployments.

For any operations requiring sudo privileges (when not running as root), you must export the sudo password as an environment variable:

```bash
export INVOKE_SUDO_PASSWORD=your_sudo_password
```

This applies to all non-root operations including:
- System administration tasks
- Package installations  
- Service management
- Configuration file updates

---

## Output Control & Debugging

Python Cloudy features a smart output system that provides clean, professional command execution while maintaining full debugging capabilities when needed.

**⚡ Quick Start**: Use `CLOUDY_VERBOSE=1` before any command to see full output:
```bash
# Example: PostgreSQL installation with verbose output
CLOUDY_VERBOSE=1 fab -H root@10.10.10.198 recipe.psql-install --cfg-paths="./.cloudy.psql"

# Example: System update with verbose output  
CLOUDY_VERBOSE=1 fab -H admin@server:22022 sys.update
```

### Output Control Modes

#### Default Mode (Smart Output)
By default, Python Cloudy intelligently categorizes commands:
- **Shows**: Status commands (`ufw status`, `systemctl status`, `df`, `ps`, etc.)
- **Hides**: Noisy installation commands (`apt install`, `wget`, `make`, `pip install`, etc.)
- **Indicators**: Success (✅) or failure (❌) messages for hidden commands

```bash
# Clean output - hides installation noise, shows status information
fab -H admin@server:22022 db.pg.install
fab -H admin@server:22022 fw.status  # Always shows output
```

#### Verbose Mode
Shows all command output for debugging and troubleshooting. **Note: Fabric does not have a `--verbose` flag**, so use the environment variable:

```bash
# Show all command output using environment variable
export CLOUDY_VERBOSE=1
fab -H admin@server:22022 db.pg.install
fab -H admin@server:22022 sys.update

# Or inline for single command
CLOUDY_VERBOSE=1 fab -H admin@server:22022 db.pg.install

# Clear verbose mode
unset CLOUDY_VERBOSE
```

#### Debug Mode  
Enables Fabric's built-in debug mode plus all command output:

```bash
# Enable debug mode with full output
fab -H admin@server:22022 --debug db.pg.install
fab -H admin@server:22022 -d fw.secure-server
```

#### Echo Mode
Echo commands before execution (Fabric built-in):

```bash
# Echo commands before running
fab -H admin@server:22022 --echo sys.hostname --hostname=myserver
fab -H admin@server:22022 -e web.nginx.install
```

### Recipe Success Messages

All deployment recipes provide comprehensive success summaries:

```bash
fab -H root@server recipe.gen-install --cfg-file="./.cloudy.generic"
```

**Example Output:**
```
🎉 ✅ GENERIC SERVER SETUP COMPLETED SUCCESSFULLY!
📋 Configuration Summary:
   ├── Hostname: myserver.example.com
   ├── Timezone: America/New_York
   ├── Admin User: admin (groups: admin,www-data)
   ├── SSH Port: 22022
   ├── Root Login: Disabled
   ├── SSH Keys: Configured
   └── Firewall: UFW enabled and configured

🚀 Generic server foundation is ready for specialized deployments!
   └── SSH Access: admin@server:22022 (key-based authentication)
```

### Environment Variables

For programmatic control, you can use environment variables:

```bash
# Enable verbose output via environment variable (RECOMMENDED)
export CLOUDY_VERBOSE=1
fab -H server sys.update

# Or use inline for single commands
CLOUDY_VERBOSE=1 fab -H server sys.update

# Clear verbose mode
unset CLOUDY_VERBOSE
```

**Note**: `CLOUDY_VERBOSE=1` is the recommended way to enable verbose output since Fabric does not have a built-in `--verbose` flag.

### Best Practices

- **Development**: Use `CLOUDY_VERBOSE=1` or `--debug` when troubleshooting issues
- **Production**: Use default mode for clean output and success confirmations  
- **Automation**: Set `CLOUDY_VERBOSE=1` in CI/CD environments for full logs
- **Learning**: Use `--echo` to see exact commands being executed

### Quick Reference

```bash
# Default mode (clean output)
fab -H server sys.update

# Verbose mode (show all output)
CLOUDY_VERBOSE=1 fab -H server sys.update

# Debug mode (Fabric debug + all output)
fab -H server --debug sys.update

# Echo mode (show commands before running)
fab -H server --echo sys.update
```

---

## Usage Examples

### Secure Server Deployment Workflow

**⚠️ IMPORTANT**: Python Cloudy implements a secure two-phase deployment:

#### Phase 1: Initial Setup (as root)
```bash
# Setup secure server - creates admin user, disables root login, configures firewall
source .venv/bin/activate
fab -H root@10.10.10.198 recipe.gen-install --cfg-file="./.cloudy.generic"
```

**After this step:**
- ✅ Root login is disabled for security
- ✅ Admin user created with SSH key authentication  
- ✅ SSH port changed (default: 22022)
- ✅ UFW firewall configured

#### Phase 2: Ongoing Management (as admin user)

**⚠️ CRITICAL**: Due to underlying Fabric issues, for any sudo operations, you must export the password as an environment variable since interactive password prompts are not supported:

```bash
# Set sudo password for automation (REQUIRED for sudo operations)
export INVOKE_SUDO_PASSWORD=your_admin_password

# Install additional services (Nginx, PostgreSQL, etc.)
fab -H admin@10.10.10.198:22022 web.nginx.install
fab -H admin@10.10.10.198:22022 db.pg.install
fab -H admin@10.10.10.198:22022 fw.allow-http
fab -H admin@10.10.10.198:22022 fw.allow-https

# Use environment variable for verbose output or --debug flag
CLOUDY_VERBOSE=1 fab -H admin@10.10.10.198:22022 db.pg.status
fab -H admin@10.10.10.198:22022 --debug fw.status
```

### Other High-Level Recipes
```bash
# Redis cache server setup
fab -H root@server.com recipe.redis-install --cfg-file="./.cloudy.redis"

# Django web server setup  
fab -H root@web.com recipe.web-install --cfg-file="./.cloudy.web"

# PostgreSQL + PostGIS database setup
fab -H root@db.com recipe.psql-install --cfg-file="./.cloudy.db"

# Use environment variable to see detailed installation progress
CLOUDY_VERBOSE=1 fab -H root@server.com recipe.redis-install --cfg-file="./.cloudy.redis"
```

### Database Management
```bash
# PostgreSQL operations
fab -H root@db.com db.pg.create-user --username=myuser --password=secure123
fab -H root@db.com db.pg.create-db --database=myapp --owner=myuser
fab -H root@db.com db.pg.grant-privs --database=myapp --username=myuser

# MySQL operations  
fab -H root@db.com db.my.install
fab -H root@db.com db.my.create-db --database=wordpress
fab -H root@db.com db.my.create-user --username=wpuser --password=pass123
```

### System Administration
```bash
# For non-root users, export sudo password first
export INVOKE_SUDO_PASSWORD=your_sudo_password

# System setup and updates
fab -H root@server.com sys.init
fab -H root@server.com sys.update
fab -H root@server.com sys.hostname --hostname=myserver.example.com

# User management
fab -H root@server.com sys.add-user --username=deploy
fab -H root@server.com sys.add-sudoer --username=deploy

# SSH configuration
fab -H root@server.com sys.ssh-port --port=2222
fab -H root@server.com sys.ssh-disable-root

# Use --echo to see exact commands being executed
fab -H root@server.com --echo sys.hostname --hostname=myserver.example.com

# System status checks (always show output)
fab -H admin@server:22022 sys.services  # Shows service status
fab -H admin@server:22022 sys.memory-usage  # Shows memory info
```

### Firewall & Security
```bash
# Firewall setup
fab -H root@server.com fw.install
fab -H root@server.com fw.secure-server --ssh-port=2222
fab -H root@server.com fw.allow-http
fab -H root@server.com fw.allow-https
fab -H root@server.com fw.allow-postgresql
```

### Web Server Setup
```bash
# Nginx setup
fab -H root@web.com web.nginx.install
fab -H root@web.com web.nginx.setup-domain --domain=example.com --proto=https

# Apache setup
fab -H root@web.com web.apache.install
fab -H root@web.com web.apache.configure-domain --domain=mysite.com

# Site management
fab -H root@web.com web.site.create-site-dir --domain=example.com
fab -H root@web.com web.site.create-venv --domain=example.com
```

### Cloud Management (AWS)
```bash
# EC2 instance management
fab aws.list-nodes
fab aws.create-node --name=web-server --image=ami-12345 --size=t3.micro
fab aws.get-node --name=web-server
fab aws.destroy-node --name=web-server
```

### Service Management
```bash
# Docker setup
fab -H root@server.com services.docker.install
fab -H root@server.com services.docker.add-user --username=deploy

# Redis configuration
fab -H root@server.com services.cache.install
fab -H root@server.com services.cache.configure
fab -H root@server.com services.cache.password --password=redis123

# VPN setup
fab -H root@vpn.com services.vpn.docker-install
fab -H root@vpn.com services.vpn.create-client --name=user1
```

---

## Command Structure

Python Cloudy organizes commands into intuitive hierarchical namespaces:

- **`recipe.*`** - High-level deployment recipes (7 commands)
- **`sys.*`** - System administration (31 commands)  
- **`db.*`** - Database management (31 commands)
  - `db.pg.*` - PostgreSQL (17 commands)
  - `db.my.*` - MySQL (7 commands)
  - `db.pgb.*` - PgBouncer (3 commands)
  - `db.pgp.*` - PgPool (2 commands)
  - `db.gis.*` - PostGIS (4 commands)
- **`web.*`** - Web servers (13 commands)
- **`fw.*`** - Firewall (9 commands)
- **`services.*`** - Service management (17 commands)
- **`aws.*`** - Cloud management (16 commands)

### Global Flags (Available for any command)

- **`--debug, -d`** - Enable Fabric debug mode + all output  
- **`--echo, -e`** - Echo commands before running (Fabric built-in)
- **`CLOUDY_VERBOSE=1`** - Environment variable for verbose output

### List All Commands
```bash
fab -l                    # Show all available commands
fab -l | grep "recipe\."  # Show only recipe commands
fab -l | grep "db\.pg\."  # Show only PostgreSQL commands

# Get help for Python Cloudy features
fab help                  # Show comprehensive help with examples
```

---

## Configuration

Python Cloudy uses hierarchical configuration files with INI format:

### Configuration Precedence (lowest to highest)
1. `cloudy/cfg/defaults.cfg` - Built-in defaults
2. `~/.cloudy` - User home directory config  
3. `./.cloudy` - Current working directory config
4. `--cfg-file` - Explicitly passed files

### Example Configuration
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
webserver-port = 8080
domain-name = example.com

[DBSERVER]
pg-version = 17
db-host = localhost
db-port = 5432
```

### Using Multiple Configs
```bash
fab -H root@server.com recipe.gen-install --cfg-file="./.cloudy.base,./.cloudy.production"
```

---

## Development

### Running Tests
```bash
./test.sh              # Run minimal test suite
python tests/test_runner.py  # Run tests directly
```

### Code Quality
```bash
./lint.sh              # Run linting (Black, isort, flake8, mypy)
```

### Environment Setup
```bash
source .venv/bin/activate    # Always activate before development
```

---

## License

Released under the [MIT](LICENSE) license.

---

## Versioning

**X.Y.Z Versioning**

- `MAJOR` version: Incompatible API changes
- `MINOR` version: Backwards-compatible functionality
- `PATCH` version: Backwards-compatible bug fixes

---

## Sponsors

[Neekware Inc](https://neekware.com)

---

## Python Compatibility

Python Cloudy is compatible with Python versions 3.8 and above. Please ensure that your environment meets this requirement before installing.

---

## Development

To contribute to Python Cloudy, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear, descriptive messages.
4. Push your branch to your fork on GitHub.
5. Submit a pull request to the main repository, detailing your changes and the problem they solve.

Please ensure that your code adheres to the existing style and conventions used in the project.
