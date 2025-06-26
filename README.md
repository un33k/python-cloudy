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

## Usage Examples

### High-Level Server Deployment
```bash
# Complete server setup with configuration file
fab -H root@10.10.10.198 recipe.gen-install --cfg-file="./.cloudy.generic"

# Redis cache server setup
fab -H root@server.com recipe.redis-install --cfg-file="./.cloudy.redis"

# Django web server setup  
fab -H root@web.com recipe.web-install --cfg-file="./.cloudy.web"

# PostgreSQL + PostGIS database setup
fab -H root@db.com recipe.psql-install --cfg-file="./.cloudy.db"
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

### List All Commands
```bash
fab -l                    # Show all available commands
fab -l | grep "recipe\."  # Show only recipe commands
fab -l | grep "db\.pg\."  # Show only PostgreSQL commands
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
