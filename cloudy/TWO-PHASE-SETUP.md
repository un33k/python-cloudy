# Two-Phase Server Setup Guide

## Overview

Ansible Cloudy now uses a **two-phase approach** to solve the "pulling the rug out from under itself" problem that occurred when the original `generic-server.yml` changed SSH settings mid-execution.

## The Problem (Solved)

Previously, `generic-server.yml` would:
1. Start as `root` on port `22`
2. Create admin user and install SSH keys
3. Change SSH port to `22022` 
4. Disable root login
5. **FAIL** - Can't continue because connection parameters changed

## The Solution

### Phase 1: Security Hardening (`hardening.yml`)
**Purpose**: Initial security setup that must run as root
**Connection**: `root` user on port `22`

**Tasks**:
- Create admin user with password
- Install SSH public key for admin user  
- Configure UFW firewall (allow new SSH port)
- Change SSH port from 22 → 22022
- Test admin user access on new port
- Disable root login
- Disable password authentication (SSH keys only)

**Result**: Server is secured, admin user ready

### Phase 2: Server Configuration (`generic-server.yml`)
**Purpose**: Complete server setup after security hardening
**Connection**: `admin` user on port `22022`

**Tasks**: 
- System configuration (hostname, timezone, swap)
- Git configuration
- Additional firewall rules
- Security packages
- Final validation

**Result**: Fully configured server ready for specialized deployments

## Usage

### Step 1: Security Hardening (Root Access)
```bash
# Run as root on port 22 (initial setup)
ansible-playbook -i inventory/test-two-phase.yml playbooks/recipes/hardening.yml --limit hardening_servers
```

### Step 2: Server Configuration (Admin Access)  
```bash
# Run as admin user on port 22022 (after hardening)
ansible-playbook -i inventory/test-two-phase.yml playbooks/recipes/generic-server.yml --limit generic_servers
```

### Step 3: Specialized Services (Admin Access)
```bash
# Deploy additional services (all use admin user on port 22022)
ansible-playbook -i inventory/test-two-phase.yml playbooks/recipes/web-server.yml
ansible-playbook -i inventory/test-two-phase.yml playbooks/recipes/database-server.yml
ansible-playbook -i inventory/test-two-phase.yml playbooks/recipes/vpn-server.yml
```

## Inventory Configuration

The `inventory/test-two-phase.yml` file contains separate host groups for each phase:

### Phase 1: `hardening_servers`
```yaml
hardening_servers:
  vars:
    ansible_user: root
    ansible_ssh_pass: pass4now  # Initial root password
    ansible_port: 22  # Initial SSH port
  hosts:
    test-generic:
      ansible_host: 10.10.10.198
      ansible_ssh_private_key_file: ~/.ssh/id_rsa  # SSH key for admin user
```

### Phase 2: `generic_servers` (and all other server types)
```yaml
generic_servers:
  vars:
    ansible_user: admin
    ansible_port: 22022  # New SSH port after hardening
    ansible_become_pass: secure123  # Sudo password for admin user
  hosts:
    test-generic:
      ansible_host: 10.10.10.198
      ansible_ssh_private_key_file: ~/.ssh/id_rsa  # SSH key authentication
```

## Configuration Variables

### Required Variables
- `admin_user`: Admin username (default: `admin`)
- `admin_password`: Admin user password
- `ssh_port`: New SSH port (default: `22022`)
- `ansible_ssh_private_key_file`: Path to SSH private key

### Security Variables
- `ssh_disable_root`: Disable root login (default: `true`)
- `ssh_enable_password_auth`: Allow password auth (default: `false`)
- `admin_groups`: Groups for admin user (default: `"admin,www-data"`)

## Benefits

✅ **Consistent Connection Context**: Each playbook runs with stable connection parameters
✅ **No Mid-Execution Failures**: No more "pulling the rug out" 
✅ **Clear Separation**: Security hardening vs. server configuration
✅ **Reusable**: Phase 2 can be run multiple times safely
✅ **Secure by Default**: SSH keys only, root disabled, custom port

## Security Features

After Phase 1 completion:
- ✅ Root login disabled (`PermitRootLogin no`)
- ✅ Admin user with SSH key authentication
- ✅ Custom SSH port (default: 22022)
- ✅ UFW firewall configured
- ✅ Password authentication disabled (SSH keys only)
- ✅ Sudo access for privileged operations

## Troubleshooting

### Connection Issues After Phase 1
If you can't connect after hardening, check:
1. SSH key is properly configured: `~/.ssh/id_rsa`
2. Admin user password is correct: `admin_password`
3. SSH port is accessible: `ssh admin@host -p 22022`
4. Firewall allows new port: `ufw status`

### Running Individual Phases
```bash
# Test Phase 1 only
ansible-playbook --check -i inventory/test-two-phase.yml hardening.yml --limit hardening_servers

# Test Phase 2 only  
ansible-playbook --check -i inventory/test-two-phase.yml generic-server.yml --limit generic_servers
```

## Migration from Old Approach

If you have existing servers set up with the old single-phase approach:
1. They should already be hardened
2. Update your inventory to use `admin` user and port `22022`
3. Run only Phase 2 (`generic-server.yml`) for additional configuration
4. Use the new two-phase approach for fresh server deployments