# Cloudy Ansible - Usage Guide

Complete step-by-step guide for using Cloudy infrastructure automation with Ansible.

## Table of Contents
- [Ali CLI Command Reference](#ali-cli-command-reference)
- [Prerequisites](#prerequisites)
- [First-Time Setup](#first-time-setup)
- [Server Deployment Workflows](#server-deployment-workflows)
- [Output Control](#output-control)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)

## Ali CLI Command Reference

Complete reference for all Ali (Ansible Line Interpreter) commands.

### 🎯 Recipe Commands

#### Core Infrastructure
```bash
./ali security          # Initial server security setup (admin user, SSH keys, firewall)
./ali base              # Basic server configuration (hostname, git, timezone, swap)
```

#### Database Services  
```bash
./ali psql              # PostgreSQL database server
./ali postgis           # PostgreSQL with PostGIS extensions
```

#### Web Services
```bash
./ali django           # Django web application server
./ali nginx            # Nginx load balancer
```

#### Cache & VPN
```bash
./ali redis            # Redis cache server  
./ali openvpn          # OpenVPN server
```

### 🛠️ Development Commands

```bash
./ali dev validate      # Comprehensive validation suite
./ali dev syntax        # Quick syntax checking  
./ali dev lint          # Ansible-lint validation
./ali dev test          # Authentication flow testing
./ali dev spell         # Spell check documentation
```

### ⚙️ Global Options

Available with any recipe command:

```bash
--prod, --production    # Use production inventory (default: test)
--check, --dry-run      # Run in check mode without changes
--verbose, -v           # Enable verbose output
--list, -l             # List available commands
--help, -h             # Show help information
```

### 🎨 Usage Examples

#### Basic Recipe Execution
```bash
./ali security         # Run on test environment
./ali django --prod    # Run on production  
./ali redis --check    # Dry run validation
```

#### Development Workflow
```bash
./ali dev syntax       # Quick validation
./ali dev validate     # Full validation  
./ali dev spell        # Check spelling
./ali dev test         # Test auth flow
```

#### Advanced Usage  
```bash
./ali nginx -- --tags ssl              # Pass ansible-playbook args
./ali django --prod --verbose          # Production with debug output
./ali security --check -- --limit web  # Dry run on specific hosts
```

#### Discovery Commands
```bash
./ali --list           # Show all recipes
./ali dev              # Show all dev commands  
./ali --help           # Show complete usage
```

### 📊 Command Summary

| **Category** | **Commands** | **Count** |
|-------------|-------------|-----------|
| **Core** | security, base | 2 |
| **Database** | psql, postgis | 2 |
| **Web** | django, nginx | 2 |
| **Services** | redis, openvpn | 2 |
| **Development** | validate, syntax, lint, test, spell | 5 |
| **Total** | | **13 commands** |

## Prerequisites

### Option 1: Quick Setup (Recommended)
```bash
# Bootstrap creates .venv and installs everything needed
./bootstrap.sh

# Activate environment
source .venv/bin/activate

# Verify installation
./ali dev syntax
```

### Option 2: Manual Setup
```bash
# Install Ansible globally (not recommended for development)
pip install ansible

# Verify installation
ansible --version
```

### SSH Key Setup
```bash
# Generate SSH key pair (if not already present)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Verify key exists
ls -la ~/.ssh/id_rsa*
```

### Server Requirements
- Fresh Ubuntu/Debian server
- Root access with password
- Network connectivity to server

## First-Time Setup

### 1. Configure Inventory
Edit `inventory/test-recipes.yml` with your server details:

```yaml
all:
  vars:
    # For INITIAL setup (fresh servers)
    ansible_user: root
    ansible_ssh_pass: your_root_password
    ansible_port: 22
    
  children:
    generic_servers:
      hosts:
        my-server:
          ansible_host: 192.168.1.100
          hostname: my-server.example.com
          admin_user: admin
          admin_password: secure_admin_password
          ssh_port: 22022
```

### 2. Test Connectivity
```bash
# Test initial connection
ansible -i inventory/test-recipes.yml my-server -m ping
```

### 3. Run Authentication Test
```bash
# Test the complete authentication flow
ansible-playbook -i inventory/test-recipes.yml test-simple-auth.yml
```

If successful, you'll see:
```
TASK [Display success] *****
ok: [my-server] => {
    "msg": "🎉 ✅ AUTHENTICATION SETUP COMPLETED!"
}
```

### 4. Update Inventory for Production Use
After successful authentication setup, update inventory:

```yaml
all:
  vars:
    # For PRODUCTION use (after setup)
    ansible_user: admin
    ansible_ssh_pass: secure_admin_password
    ansible_port: 22022
```

## Server Deployment Workflows

### Generic Server (Foundation)
Sets up secure SSH, user management, and firewall.

```bash
# Deploy secure foundation
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

**What it does:**
- ✅ Creates admin user with SSH key access
- ✅ Configures UFW firewall 
- ✅ Changes SSH port to 22022
- ✅ Disables root login
- ✅ Sets up sudo access

### VPN Server
Deploys OpenVPN using Docker containers.

```bash
# Deploy VPN server
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/vpn-server.yml
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Docker installation
- ✅ OpenVPN container setup
- ✅ Client certificate management
- ✅ Firewall rules for VPN traffic

### Web Server
Complete web application stack.

```bash
# Deploy web server
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/web-server.yml
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Nginx web server
- ✅ Apache configuration
- ✅ Supervisor process management
- ✅ SSL certificate support

### Database Server
PostgreSQL with spatial extensions.

```bash
# Deploy database server
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/database-server.yml
```

**What it includes:**
- ✅ Generic server foundation
- ✅ PostgreSQL installation
- ✅ PostGIS spatial extensions
- ✅ PgBouncer connection pooling
- ✅ Database user management

### Cache Server
Redis caching solution.

```bash
# Deploy cache server
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/cache-server.yml
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Redis installation
- ✅ Memory optimization
- ✅ Persistence configuration

### Load Balancer
Nginx load balancer with SSL.

```bash
# Deploy load balancer
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/load-balancer.yml
```

**What it includes:**
- ✅ Generic server foundation
- ✅ Nginx load balancer
- ✅ SSL termination
- ✅ Backend server configuration

## Output Control

### Default Output (Clean)
Shows only changes and failures:
```bash
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

### Compact Output
Single line per task:
```bash
ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

### One-Line Output
Extremely compact:
```bash
ANSIBLE_STDOUT_CALLBACK=oneline ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

### Verbose Output
Full debugging information:
```bash
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml -v
```

### Ultra-Verbose Output
Maximum detail:
```bash
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml -vvv
```

## Common Scenarios

### Scenario 1: Complete Web Application Stack

```bash
# 1. Start with fresh server, deploy foundation
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml

# 2. Update inventory to use admin user on port 22022
# Edit inventory/test-recipes.yml: ansible_user: admin, ansible_port: 22022

# 3. Deploy database layer
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/database-server.yml

# 4. Deploy web application layer
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/web-server.yml

# 5. Optional: Deploy load balancer
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/load-balancer.yml
```

### Scenario 2: VPN-Only Server

```bash
# Single command deployment
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/vpn-server.yml

# Update inventory for admin user access
# Edit inventory: ansible_user: admin, ansible_port: 22022
```

### Scenario 3: Cache-Only Server

```bash
# Deploy Redis cache server
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/cache-server.yml

# Update inventory for admin user access
# Edit inventory: ansible_user: admin, ansible_port: 22022
```

### Scenario 4: Multi-Server Environment

Create separate inventory files:

**inventory/production-web.yml:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: admin_password
    ansible_port: 22022
    
  children:
    web_servers:
      hosts:
        web1:
          ansible_host: 10.0.1.10
        web2:
          ansible_host: 10.0.1.11
```

**inventory/production-db.yml:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_ssh_pass: admin_password
    ansible_port: 22022
    
  children:
    database_servers:
      hosts:
        db1:
          ansible_host: 10.0.2.10
```

Deploy:
```bash
# Deploy web servers
ansible-playbook -i inventory/production-web.yml playbooks/recipes/web-server.yml

# Deploy database servers
ansible-playbook -i inventory/production-db.yml playbooks/recipes/database-server.yml
```

## Troubleshooting

### Connection Issues

**Problem:** `UNREACHABLE! => ssh: connect to host X port Y: Connection refused`

**Solutions:**
1. Check server is running: `ping server_ip`
2. Verify SSH port: `nmap -p 22,22022 server_ip`
3. Check inventory configuration matches server state
4. For fresh servers, use `ansible_user: root` and `ansible_port: 22`
5. After setup, use `ansible_user: admin` and `ansible_port: 22022`

### Authentication Issues

**Problem:** `Permission denied (publickey,password)`

**Solutions:**
1. Verify password in inventory is correct
2. Check SSH key exists: `ls ~/.ssh/id_rsa*`
3. For fresh servers, ensure `ansible_user: root`
4. After setup, ensure `ansible_user: admin`

### Firewall Issues

**Problem:** SSH connection timeout after port change

**Solutions:**
1. The recipes automatically configure UFW firewall
2. Port 22022 is opened before SSH port change
3. If locked out, reset server to fresh state and retry

### Task Failures

**Problem:** Tasks fail during execution

**Solutions:**
1. Run with verbose output: `ansible-playbook ... -v`
2. Check specific task error messages
3. Verify server has sufficient resources (disk, memory)
4. Check internet connectivity for package downloads

### Output Too Verbose

**Problem:** Too much output information

**Solutions:**
1. Use default clean output (configured in `ansible.cfg`)
2. Try minimal callback: `ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook ...`
3. Focus on changed tasks only (default behavior)

### Re-running Playbooks

**Best Practice:** Ansible playbooks are idempotent - safe to re-run.

```bash
# Re-run safely - only changes will be applied
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

### Testing Before Production

**Always test authentication flow first:**
```bash
# Test on fresh server
ansible-playbook -i inventory/test-recipes.yml test-simple-auth.yml

# If successful, proceed with full recipe
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml
```

## Advanced Usage

### Custom Configuration Variables

Add custom variables to inventory:
```yaml
all:
  vars:
    custom_domain: myapp.com
    ssl_cert_email: admin@myapp.com
    
  children:
    web_servers:
      hosts:
        web1:
          ansible_host: 10.0.1.10
          app_name: myapp-production
```

### Running Specific Tasks

Use tags to run specific parts:
```bash
# Run only SSH configuration
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml --tags ssh

# Run only firewall setup
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml --tags firewall
```

### Dry Run Mode

Test without making changes:
```bash
# Check what would change
ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml --check
```

This guide covers the most common usage patterns. For detailed command reference, see `CLAUDE.md`.