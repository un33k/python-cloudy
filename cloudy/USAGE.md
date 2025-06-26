# Cloudy Ansible - Usage Guide

## Quick Start

### 1. Setup Inventory
```bash
# Copy example inventory
cp inventory/example-production.yml inventory/hosts.yml

# Edit with your server details
vim inventory/hosts.yml
```

### 2. Run Individual Tasks (Granular Operations)
```bash
# System operations
ansible-playbook tasks/sys/core/update.yml -i inventory/hosts.yml
ansible-playbook tasks/sys/user/add-user.yml -e "username=deploy" -i inventory/hosts.yml
ansible-playbook tasks/sys/ssh/set-port.yml -e "ssh_port=2222" -i inventory/hosts.yml

# Database operations
ansible-playbook tasks/db/postgresql/install.yml -e "pg_version=17" -i inventory/hosts.yml
ansible-playbook tasks/db/postgresql/create-user.yml -e "username=myapp password=secret" -i inventory/hosts.yml
ansible-playbook tasks/db/mysql/install-server.yml -i inventory/hosts.yml

# Service operations
ansible-playbook tasks/services/redis/install.yml -i inventory/hosts.yml
ansible-playbook tasks/sys/firewall/allow-http.yml -i inventory/hosts.yml
```

### 3. Run Complete Recipes (Full Deployments)
```bash
# Generic server setup
ansible-playbook playbooks/recipes/generic-server.yml -i inventory/hosts.yml

# Database server setup
ansible-playbook playbooks/recipes/database-server.yml -l database_servers -i inventory/hosts.yml

# Target specific hosts
ansible-playbook playbooks/recipes/generic-server.yml -l bastion -i inventory/hosts.yml
```

### 4. Use Tags for Partial Deployments
```bash
# Only user management
ansible-playbook playbooks/recipes/generic-server.yml --tags users -i inventory/hosts.yml

# Only security setup
ansible-playbook playbooks/recipes/generic-server.yml --tags security,firewall -i inventory/hosts.yml

# Skip firewall setup
ansible-playbook playbooks/recipes/generic-server.yml --skip-tags firewall -i inventory/hosts.yml
```

## Common Workflows

### Initial Server Setup
```bash
# 1. Basic server foundation
ansible-playbook playbooks/recipes/generic-server.yml -l new_server -i inventory/hosts.yml

# 2. Install database if needed
ansible-playbook playbooks/recipes/database-server.yml -l new_server -i inventory/hosts.yml
```

### Database Management
```bash
# Create new database and user
ansible-playbook tasks/db/postgresql/create-database.yml -e "database=newapp owner=newapp_user" -l db-primary
ansible-playbook tasks/db/postgresql/create-user.yml -e "username=newapp_user password=secret123" -l db-primary
ansible-playbook tasks/db/postgresql/grant-privileges.yml -e "database=newapp username=newapp_user" -l db-primary

# Backup database
ansible-playbook tasks/db/postgresql/dump-database.yml -e "database=myapp dump_file=/backup/myapp.sql" -l db-primary
```

### User Management
```bash
# Add new team member
ansible-playbook tasks/sys/user/add-user.yml -e "username=john" -i inventory/hosts.yml
ansible-playbook tasks/sys/user/change-password.yml -e "username=john password=temp123" -i inventory/hosts.yml
ansible-playbook tasks/sys/user/add-sudoer.yml -e "username=john" -i inventory/hosts.yml
ansible-playbook tasks/sys/ssh/push-public-key.yml -e "target_user=john pub_key_path=~/.ssh/john_rsa.pub" -i inventory/hosts.yml
```

### Firewall Management
```bash
# Open application ports
ansible-playbook tasks/sys/firewall/allow-port.yml -e "port=8080" -i inventory/hosts.yml
ansible-playbook tasks/sys/firewall/allow-http.yml -i inventory/hosts.yml
ansible-playbook tasks/sys/firewall/allow-https.yml -i inventory/hosts.yml

# Database access
ansible-playbook tasks/sys/firewall/allow-postgresql.yml -l database_servers -i inventory/hosts.yml
```

### Service Management
```bash
# Redis setup
ansible-playbook tasks/services/redis/install.yml -l cache_servers -i inventory/hosts.yml
ansible-playbook tasks/services/redis/configure-memory.yml -e "memory_mb=2048" -l cache_servers -i inventory/hosts.yml
ansible-playbook tasks/services/redis/configure-port.yml -e "redis_port=6380" -l cache_servers -i inventory/hosts.yml

# Docker setup
ansible-playbook tasks/sys/docker/install.yml -l web_servers -i inventory/hosts.yml
ansible-playbook tasks/sys/docker/add-user.yml -e "username=deploy" -l web_servers -i inventory/hosts.yml
```

## Advanced Usage

### Dry Run (Check Mode)
```bash
# Test what would change
ansible-playbook playbooks/recipes/generic-server.yml --check -i inventory/hosts.yml
```

### Verbose Output
```bash
# See detailed execution
ansible-playbook playbooks/recipes/generic-server.yml -v -i inventory/hosts.yml
ansible-playbook playbooks/recipes/generic-server.yml -vvv -i inventory/hosts.yml  # Very verbose
```

### Variable Override
```bash
# Override inventory variables
ansible-playbook playbooks/recipes/database-server.yml -e "pg_version=16" -e "setup_mysql=true" -i inventory/hosts.yml
```

### Limit to Specific Hosts
```bash
# Single host
ansible-playbook playbooks/recipes/generic-server.yml -l db-primary -i inventory/hosts.yml

# Multiple hosts
ansible-playbook playbooks/recipes/generic-server.yml -l "web-01,web-02" -i inventory/hosts.yml

# Host pattern
ansible-playbook playbooks/recipes/generic-server.yml -l "web-*" -i inventory/hosts.yml
```

## Task Categories

### System Tasks (78 tasks)
- **Core**: init, update, upgrade, git, packages, services, hostname
- **Users**: add, delete, password, sudo, groups
- **SSH**: port, auth, keys, security
- **Firewall**: install, rules, ports, protocols
- **Security**: fail2ban, hardening
- **Services**: docker, redis, memcached
- **System**: timezone, swap, editor

### Database Tasks (23 tasks)
- **PostgreSQL**: install, users, databases, privileges, clusters, dump
- **MySQL**: install, users, databases, privileges, root password

### Available Recipes
- **generic-server.yml**: Complete server foundation
- **database-server.yml**: Database server with PostgreSQL/MySQL/Redis

## Tips

1. **Always use inventory files** instead of `-H` for better organization
2. **Use tags** to run specific parts of recipes
3. **Test with --check** before running on production
4. **Use vault for sensitive variables** like passwords
5. **Combine granular tasks** for custom workflows
6. **Use -l** to limit execution to specific hosts