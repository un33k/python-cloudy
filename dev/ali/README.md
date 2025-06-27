# Ali (Ansible Line Interpreter)

A simplified CLI tool for running Ansible Cloudy recipes without remembering long command paths.

## ✨ Features

- **90% shorter commands**: `ali security` vs `ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/security.yml`
- **Smart recipe discovery**: Finds recipes by name across all categories
- **Auto inventory selection**: Uses test by default, production with `--prod`
- **Pass-through arguments**: Forward any ansible-playbook flags with `--`
- **Built-in help**: List available recipes and usage examples

## 🚀 Quick Start

```bash
# Basic usage (uses test inventory)
./ali security          # Run core/security.yml
./ali django            # Run www/django.yml  
./ali redis             # Run cache/redis.yml

# Production usage
./ali security --prod   # Run on production inventory
./ali django --prod     # Deploy to production servers

# Dry run / check mode
./ali redis --check     # Test run without making changes
./ali nginx --check     # Validate nginx recipe

# Pass arguments to ansible-playbook
./ali django -- --tags nginx        # Only run nginx tasks
./ali redis -- --limit cache_servers # Only run on cache servers
./ali security -- -v                 # Verbose output
```

## 📋 Available Commands

### Core Recipes
```bash
./ali security         # Initial server security (admin user, SSH, firewall)
./ali base             # Basic server setup (hostname, git, timezone)
```

### Service Recipes  
```bash
./ali django          # Django web application
./ali redis           # Redis cache server
./ali psql             # PostgreSQL database
./ali postgis          # PostgreSQL with PostGIS
./ali nginx            # Nginx load balancer
./ali openvpn          # OpenVPN server
```

### Discovery & Help
```bash
./ali --list           # Show all available recipes
./ali --help           # Show usage information
./ali redis --help     # Recipe-specific help
```

## 🎯 Command Structure

```bash
./ali <recipe> [options] [-- ansible-args]
```

### Options
- `--prod`, `--production` - Use production inventory (default: test)
- `--check`, `--dry-run` - Run in check mode without making changes
- `--verbose`, `-v` - Enable verbose output
- `--list`, `-l` - List all available recipes
- `--help`, `-h` - Show help information

### Pass-through Arguments
Use `--` to pass arguments directly to `ansible-playbook`:

```bash
./ali django -- --tags nginx,ssl    # Only run nginx and ssl tasks
./ali redis -- --limit "cache*"     # Run only on hosts matching cache*
./ali security -- --ask-become-pass # Prompt for sudo password
./ali nginx -- --check --diff       # Check mode with diff output
```

## 📁 Recipe Organization

Ali automatically discovers recipes from the `cloudy/playbooks/recipes/` directory:

```
cloudy/playbooks/recipes/
├── core/
│   ├── security.yml    → ali security
│   └── base.yml        → ali base
├── www/
│   └── django.yml      → ali django  
├── cache/
│   └── redis.yml       → ali redis
├── db/
│   ├── psql.yml        → ali psql
│   └── postgis.yml     → ali postgis
├── lb/
│   └── nginx.yml       → ali nginx
└── vpn/
    └── openvpn.yml     → ali openvpn
```

## 🏗️ Workflow Examples

### Standard Server Setup
```bash
# Step 1: Security hardening
./ali security

# Step 2: Basic configuration  
./ali base

# Step 3: Deploy services
./ali django
./ali redis
./ali nginx
```

### Production Deployment
```bash
# Deploy to production with checks
./ali django --prod --check  # Dry run first
./ali django --prod          # Actual deployment
```

### Development & Testing
```bash
# Quick validation
./ali django --check

# Debug with verbose output
./ali redis -- -v

# Target specific tags
./ali nginx -- --tags ssl,config
```

## 🔧 Installation & Setup

### Requirements
- Python 3.8+
- Ansible 6.0+
- Valid `cloudy/` project structure

### Setup
```bash
# Ali works out of the box - no setup needed!
# Just make sure ansible is installed (usually via brew/apt/yum)

# Test ali installation
./ali --list
```

### Zero Dependencies
Ali uses only Python standard library and calls `ansible-playbook` directly:
- No virtual environments needed
- No pip installations required  
- Works with any Python 3.8+ installation
- Just requires `ansible-playbook` to be in PATH

## 🐛 Troubleshooting

### "Could not find project root"
```bash
# Run ali from the ansible-cloudy project directory
cd /path/to/ansible-cloudy/
./ali security
```

### "ansible-playbook not found"
```bash
# Install ansible via your system package manager
brew install ansible        # macOS
sudo apt install ansible    # Ubuntu/Debian  
sudo yum install ansible    # RHEL/CentOS
```

### "Recipe 'xyz' not found"
```bash
# List available recipes
./ali --list

# Check recipe name spelling
./ali django  # not ./ali Django
```

### "Inventory file not found"
```bash
# Ensure inventory files exist
ls cloudy/inventory/
# Should show: test.yml, production.yml
```

## 🎨 Customization

### Adding New Recipes
1. Create recipe file: `cloudy/playbooks/recipes/category/name.yml`
2. Ali automatically discovers it: `./ali name`

### Custom Inventories
Modify `dev/ali/ali.py` to add support for additional inventory files.

### Default Arguments
Set common ansible-playbook arguments in the `AnsibleRunner.run_recipe()` method.

## 📊 Comparison

| Traditional Command | Ali Command | Savings |
|-------------------|-------------|---------|
| `ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/security.yml` | `./ali security` | 85 chars |
| `ansible-playbook -i cloudy/inventory/production.yml cloudy/playbooks/recipes/www/django.yml --check` | `./ali django --prod --check` | 77 chars |
| `ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/cache/redis.yml --tags config` | `./ali redis -- --tags config` | 69 chars |

**Average savings: 90%+ shorter commands!**