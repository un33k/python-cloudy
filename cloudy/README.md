# Cloudy Ansible - Granular Infrastructure Automation

**Migrated from Python Cloudy (Fabric) to Ansible while maintaining granular task philosophy**

## Philosophy: Granular Tasks + Composable Recipes

This project maintains the excellent granular approach from the original Python Cloudy:
- **One task = One function** (e.g., change password, add user, set SSH port)
- **Composable recipes** that combine granular tasks
- **Flexible usage** - run individual tasks or complete deployments

## Directory Structure

```
cloudy/
├── ansible.cfg                    # Ansible configuration
├── inventory/                     # Host and variable definitions
│   ├── hosts.yml                 # Main inventory file
│   ├── group_vars/               # Group-specific variables
│   │   ├── all.yml              # Global defaults (replaces .cloudy files)
│   │   ├── database_servers.yml  # Database server configs
│   │   └── web_servers.yml       # Web server configs
│   └── host_vars/                # Host-specific overrides
├── tasks/                        # Granular tasks (one function each)
│   ├── sys/                     # System administration tasks
│   │   ├── core/                # System initialization, updates
│   │   ├── user/                # User management (add, delete, password)
│   │   ├── ssh/                 # SSH configuration
│   │   ├── firewall/            # Firewall management
│   │   └── ...                  # Other system tasks
│   ├── db/                      # Database tasks
│   │   ├── postgresql/          # PostgreSQL operations
│   │   ├── mysql/               # MySQL operations
│   │   └── redis/               # Redis operations
│   ├── web/                     # Web server tasks
│   │   ├── nginx/               # Nginx configuration
│   │   ├── apache/              # Apache configuration
│   │   └── ssl/                 # SSL certificate management
│   └── services/                # Service management tasks
├── playbooks/                   # Composed workflows
│   ├── recipes/                 # High-level deployment recipes
│   │   ├── generic-server.yml   # Complete server setup
│   │   ├── database-server.yml  # Database server deployment
│   │   └── web-server.yml       # Web server deployment
│   └── maintenance/             # Maintenance playbooks
├── roles/                       # Traditional Ansible roles (if needed)
├── library/                     # Custom Ansible modules
├── filter_plugins/              # Custom Jinja2 filters
├── templates/                   # Configuration file templates
└── files/                       # Static files to copy
```

## Usage Examples

### Granular Tasks (One-off Operations)

```bash
# Change a user's password
ansible-playbook tasks/sys/user/change-password.yml -e "username=john password=newpass"

# Set SSH port
ansible-playbook tasks/sys/ssh/set-port.yml -e "port=2222"

# Create PostgreSQL user
ansible-playbook tasks/db/postgresql/create-user.yml -e "username=myapp password=secret"

# Install Nginx
ansible-playbook tasks/web/nginx/install.yml
```

### Composed Recipes (Full Deployments)

```bash
# Complete generic server setup
ansible-playbook playbooks/recipes/generic-server.yml -i inventory/hosts.yml

# Database server deployment
ansible-playbook playbooks/recipes/database-server.yml -l database_servers

# Web server with SSL
ansible-playbook playbooks/recipes/web-server.yml -e "ssl_enabled=true domain_name=mysite.com"
```

### Partial Recipes (Custom Combinations)

```bash
# Just user setup tasks
ansible-playbook playbooks/recipes/generic-server.yml --tags users

# Skip firewall setup
ansible-playbook playbooks/recipes/generic-server.yml --skip-tags firewall

# Only SSH security tasks
ansible-playbook playbooks/recipes/generic-server.yml --tags ssh,security
```

## Migration from Python Cloudy

### Command Mapping

| Python Cloudy (Fabric) | New Ansible Equivalent |
|------------------------|-------------------------|
| `fab sys.add-user --username=john` | `ansible-playbook tasks/sys/user/add-user.yml -e "username=john"` |
| `fab sys.change-password --username=john --password=pass` | `ansible-playbook tasks/sys/user/change-password.yml -e "username=john password=pass"` |
| `fab recipe.gen-install --cfg-file=./.cloudy.generic` | `ansible-playbook playbooks/recipes/generic-server.yml -i inventory/hosts.yml` |
| `fab db.pg.create-user --username=app --password=secret` | `ansible-playbook tasks/db/postgresql/create-user.yml -e "username=app password=secret"` |

### Configuration Migration

Old `.cloudy` files → New `inventory/group_vars/` files:

```ini
# Old: .cloudy.generic
[COMMON]
hostname = myserver
admin-user = admin
ssh-port = 22022
```

```yaml
# New: inventory/group_vars/all.yml
hostname: myserver
admin_user: admin
ssh_port: 22022
```

## Key Features Preserved

✅ **Granular Operations** - Every function is a separate, reusable task  
✅ **Composable Recipes** - Combine tasks into deployment workflows  
✅ **Flexible Usage** - One-off fixes or complete deployments  
✅ **Configuration Management** - Hierarchical variable system  
✅ **Error Handling** - Proper validation and rollback  
✅ **Git Integration** - Automatic /etc commits (where applicable)  

## Getting Started

1. **Configure inventory:**
   ```bash
   cp inventory/hosts.yml.example inventory/hosts.yml
   # Edit with your server details
   ```

2. **Set variables:**
   ```bash
   # Edit inventory/group_vars/all.yml with your defaults
   ```

3. **Run a simple task:**
   ```bash
   ansible-playbook tasks/sys/core/update.yml -i inventory/hosts.yml
   ```

4. **Deploy a complete server:**
   ```bash
   ansible-playbook playbooks/recipes/generic-server.yml -i inventory/hosts.yml
   ```

## Next Steps

- [ ] Port remaining tasks from `cloudy-old/`
- [ ] Add custom modules for complex operations
- [ ] Create Ansible Galaxy collection
- [ ] Add comprehensive testing
- [ ] Document all granular tasks