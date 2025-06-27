# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

```bash
# Install Ansible
pip install ansible

# Navigate to project directory
cd ansible-cloudy/
```

### Core Development Commands

#### Simplified Server Setup (Recommended) - Using Ali CLI
- **Step 1 - Security**: `./ali security` (creates admin user, SSH keys, firewall, disables root)
- **Step 2 - Core**: `./ali base` (hostname, git, timezone, swap, etc.)
- **Step 3 - Services**: `./ali django`, `./ali redis`, `./ali nginx` (deploy specific services)

#### Traditional Commands (if preferred)
- **Step 1 - Security**: `ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/security.yml`
- **Step 2 - Core**: `ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/base.yml`
- **Step 3 - Services**: `ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/[category]/[service].yml`

#### Production Setup
- **Ali CLI**: `./ali security --prod`, `./ali django --prod`, `./ali redis --prod`
- **Traditional**: `ansible-playbook -i cloudy/inventory/production.yml cloudy/playbooks/recipes/[category]/[service].yml`

#### Development Tools
- **Ali CLI**: `./ali security` - Simplified Ansible commands (90% shorter)
- **Comprehensive validation**: `./dev/validate.py` - Full validation suite for all components
- **Quick syntax check**: `./dev/syntax-check.sh` - Fast syntax validation only
- **Authentication test**: `ansible-playbook -i cloudy/inventory/test.yml dev/test-auth.yml --check`
- **Clean output**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Spell checking**: Configured via `dev/.cspell.json` with 369 technical terms
- **Linting**: Configured via `dev/.ansible-lint.yml` and `dev/.yamlint.yml`

### Simplified Server Setup

**🎯 SIMPLE APPROACH**: Three clear steps for any server.

**Workflow**:
1. **core/security.yml** → Sets up admin user, SSH keys, firewall, disables root
2. **core/base.yml** → Basic server config (hostname, git, timezone, etc.)  
3. **[category]/[service].yml** → Deploy specific services (www/django, db/psql, cache/redis, etc.)

**Security Features**:
- ✅ **Admin user**: Created with SSH key access
- ✅ **Root disabled**: No more root login after security step
- ✅ **Firewall**: UFW configured with custom SSH port
- ✅ **Simple**: No complex detection logic

### Legacy Single-Phase Setup

**⚠️ IMPORTANT**: The old single-phase approach can pull the rug out from under itself during SSH security changes.

**⚠️ CRITICAL - Sudo Password Requirements**:

Ansible requires sudo password configuration for privileged operations after switching from root to admin user. There are two ways to provide this:

#### Method 1: Inventory Configuration (Recommended)
Add the sudo password directly in your inventory file:

```yaml
generic_servers:
  hosts:
    test-generic:
      admin_password: secure123        # Login password  
      ansible_become_pass: secure123   # Sudo password
```

Then run commands normally:
```bash
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

#### Method 2: Environment Variable
Set the sudo password via environment variable:

```bash
# Set sudo password for the session
export ANSIBLE_BECOME_PASS=secure123

# Or provide it directly with the command
ANSIBLE_BECOME_PASS=secure123 ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

**SSH Key Configuration**:

For secure authentication, configure SSH keys in your inventory:

```yaml
all:
  vars:
    ansible_ssh_private_key_file: ~/.ssh/id_rsa  # SSH key for initial root connection
    
generic_servers:
  hosts:
    test-generic:
      admin_password: secure123        # Login password  
      ansible_become_pass: secure123   # Sudo password
```

**How SSH Key Installation Works**:
1. **Initial connection**: Uses `root` + SSH key (if available) or password fallback
2. **Create admin user**: Sets up admin user with password
3. **Install SSH key**: Copies the public key (`~/.ssh/id_rsa.pub`) to admin user's `~/.ssh/authorized_keys`
4. **Switch connection**: Changes to admin user with SSH key authentication
5. **Secure server**: Disables root login and password authentication

**Why This is Needed**:
- Initial connection uses `root` with SSH key authentication (preferred) or password fallback
- After admin user creation and SSH key installation, connection switches to admin user
- Admin user requires sudo password for privileged operations (firewall, system config, etc.)
- The `admin_password` is for SSH login, `ansible_become_pass` is for sudo operations
- SSH keys provide secure, passwordless authentication after setup

**Complete Secure Workflow Example**:
```bash
# 1. Setup secure server (disables root, creates admin user with SSH keys)
# Pass root password via command line (recommended for security)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml -e "ansible_ssh_pass=pass4now"

# Alternative: Prompt for password (most secure)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml --ask-pass

# 2. Deploy additional services (uses admin user authentication)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/web-server.yml
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/database-server.yml
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/cache-server.yml
```

**Security Features**:
- ✅ Root login disabled (`PermitRootLogin no`)
- ✅ Admin user with SSH key authentication
- ✅ Custom SSH port (default: 22022)
- ✅ UFW firewall configured
- ✅ Sudo access for privileged operations

**Output Control System**:
- ✅ **Default**: Shows only changes and failures (clean output)
- ✅ **Minimal**: `ANSIBLE_STDOUT_CALLBACK=minimal` (compact format)
- ✅ **One-line**: `ANSIBLE_STDOUT_CALLBACK=oneline` (single line per task)
- ✅ **Verbose**: `ansible-playbook ... -v` (detailed debugging)
- ✅ **Always Shown**: Changed tasks, failed tasks, unreachable hosts
- ✅ **Hidden by Default**: Successful unchanged tasks, skipped tasks

### Ansible Recipe Examples

```bash
# Ali CLI - Simplified Commands (Recommended)
# Step 1: Security setup
./ali security

# Step 2: Core setup  
./ali base

# Step 3: Service deployment
./ali psql
./ali django
./ali redis
./ali nginx
./ali openvpn

# Production deployment
./ali security --prod
./ali django --prod

# Dry runs and testing
./ali redis --check
./ali nginx -- --tags ssl

# Traditional Commands (if preferred)
# Step 1: Security (run as root on port 22)
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/security.yml

# Step 2: Core setup (run as admin on port 22022)  
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/base.yml

# Step 3: Service deployment (run as admin)
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/db/psql.yml
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/www/django.yml
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/cache/redis.yml
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/lb/nginx.yml
ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/vpn/openvpn.yml

# Individual task execution
ansible-playbook -i inventory/test.yml playbooks/recipes/core/base.yml --tags ssh
ansible-playbook -i inventory/test.yml playbooks/recipes/core/base.yml --tags firewall
ansible-playbook -i inventory/test.yml playbooks/recipes/www/django.yml --tags nginx

# Development and validation
./dev/validate.py                    # Comprehensive validation
./dev/syntax-check.sh               # Quick syntax check
ansible-playbook -i inventory/test.yml dev/test-auth.yml --check  # Auth flow test
ansible-playbook -i inventory/test.yml playbooks/recipes/core/base.yml --check
```

#### Recipe Categories
- **core/security.yml**: Initial server security (admin user, SSH keys, firewall, disable root)
- **core/base.yml**: Basic server configuration (hostname, git, timezone, swap)
- **db/psql.yml**: PostgreSQL database server
- **db/postgis.yml**: PostgreSQL with PostGIS extensions
- **www/django.yml**: Django web server with Nginx/Apache/Supervisor
- **cache/redis.yml**: Redis cache server
- **lb/nginx.yml**: Nginx load balancer with SSL
- **vpn/openvpn.yml**: OpenVPN server with Docker

## Architecture Overview

### Directory Structure
```
cloudy/
├── playbooks/recipes/     # High-level deployment recipes
├── tasks/                 # Modular task files
│   ├── sys/              # System operations (SSH, firewall, users)
│   ├── db/               # Database automation (PostgreSQL, MySQL)
│   ├── web/              # Web server management
│   └── services/         # Service management (Docker, Redis, VPN)
├── templates/            # Configuration file templates
├── inventory/            # Server inventory configurations
└── ansible.cfg          # Ansible configuration
```

### Configuration System
Server configurations are defined in YAML inventory files:

**inventory/test-recipes.yml:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: secure123
    ansible_port: 22022
    
  children:
    generic_servers:
      hosts:
        production-web:
          ansible_host: 10.10.10.100
          hostname: web.example.com
          admin_user: admin
          admin_password: secure123
          ssh_port: 22022
```

### Recipe Pattern
Recipes are high-level Ansible playbooks that:
- Include multiple task files in logical order
- Use inventory variables for configuration
- Provide idempotent server deployment
- Include error handling and validation

Example recipe structure:
```yaml
---
- name: Deploy Generic Server
  hosts: generic_servers
  become: true
  
  tasks:
    - include_tasks: ../tasks/sys/core/update.yml
    - include_tasks: ../tasks/sys/user/add-user.yml
    - include_tasks: ../tasks/sys/ssh/install-public-key.yml
    - include_tasks: ../tasks/sys/firewall/install.yml
```

## Development Requirements

- **Ansible**: ≥2.9
- **Python**: ≥3.8 (for Ansible)
- **SSH Access**: To target servers
- **Development tools**: VS Code with Ansible extension recommended

## Ansible Migration Commands

### Environment Setup for Ansible
```bash
# Ensure Ansible is installed
pip install ansible

# Navigate to Ansible implementation
cd ansible-cloudy/
```

### Core Ansible Commands
- **Run recipe playbooks**: `ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/[recipe-name].yml`
- **Test authentication flow**: `ansible-playbook -i inventory/test-recipes.yml test-simple-auth.yml`
- **Clean output (changes only)**: Configured in `ansible.cfg` with `display_skipped_hosts = no`
- **Alternative output formats**:
  - `ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook ...` (compact format)
  - `ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook ...` (one line per task)
  - Standard verbose: `ansible-playbook ... -v` (detailed debugging)

### Ansible Recipe Examples
```bash
# Generic server setup (secure SSH, user management, firewall)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml

# VPN server setup (OpenVPN with Docker)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/vpn-server.yml

# Web server setup (Nginx, Apache, Supervisor)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/web-server.yml

# Database server setup (PostgreSQL, PostGIS, PgBouncer)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/database-server.yml

# Cache server setup (Redis)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/cache-server.yml

# Load balancer setup (Nginx with SSL)
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/load-balancer.yml
```

### Ansible Security Features
- ✅ **Safe Authentication Flow**: UFW firewall configured before SSH port changes
- ✅ **SSH Key Management**: Automated public key installation and validation
- ✅ **Connection Transition**: Seamless root-to-admin user switching
- ✅ **Firewall Integration**: Port 22022 opened before SSH service restart
- ✅ **Sudo Configuration**: NOPASSWD sudo access for admin operations
- ✅ **Root Login Disable**: Safely disabled after admin user verification

### Ansible Inventory Configuration
The `inventory/test-recipes.yml` file configures connection parameters:
```yaml
all:
  vars:
    ansible_user: admin          # Connect as admin user (after setup)
    ansible_ssh_pass: secure123  # Admin password
    ansible_port: 22022          # Custom SSH port
    ansible_host_key_checking: false
    
  children:
    generic_servers:
      hosts:
        test-generic:
          ansible_host: 10.10.10.198
          hostname: test-generic.example.com
          admin_user: admin
          admin_password: secure123
          ssh_port: 22022
```

### Ansible Output Control
The `ansible.cfg` file is configured for clean output:
```ini
[defaults]
host_key_checking = False
display_skipped_hosts = no    # Hide successful/unchanged tasks
display_ok_hosts = no         # Show only changes and failures
```

This shows only:
- ✅ **CHANGED** tasks (what modified the server)
- ❌ **FAILED** tasks (what went wrong)  
- ⏭️ **UNREACHABLE** hosts (connection issues)