# Development Tools

This directory contains essential development tools for Ansible Cloudy.

## Quick Start

```bash
# From the project root directory
cd ansible-cloudy/

# Validate everything
./dev/validate.py

# Quick syntax check only
./dev/syntax-check.sh

# Test authentication flow
ansible-playbook -i cloudy/inventory/test.yml dev/test-auth.yml --check
```

## Tools Overview

### 🔍 validate.py
**Comprehensive validation suite** - Validates all components of the Ansible setup.

**What it checks:**
- ✅ Simplified directory structure 
- ✅ YAML syntax for all files
- ✅ Task file structure
- ✅ Recipe/playbook structure  
- ✅ Inventory file parsing
- ✅ Template files
- ✅ Recipe dependencies
- ✅ Ansible syntax validation

**Usage:**
```bash
# From project root
./dev/validate.py
```

**Example output:**
```
🧪 Running Ansible Cloudy Validation Suite (Simplified)...
============================================================

✅ PASSED: Simplified Structure
✅ PASSED: Task File Structure  
✅ PASSED: Recipe Files
✅ PASSED: Inventory Files
✅ PASSED: Template Files
✅ PASSED: Recipe Dependencies
✅ PASSED: Ansible Syntax

🎉 All validations passed!
✅ Ansible Cloudy is ready for deployment
```

### ⚡ syntax-check.sh
**Quick syntax checker** - Fast validation of playbook syntax only.

**What it checks:**
- ✅ Core recipes syntax
- ✅ Service recipes syntax  
- ✅ Dev files syntax

**Usage:**
```bash
# From project root
./dev/syntax-check.sh
```

**Example output:**
```
🔍 Quick Ansible Syntax Check
===============================

Checking core recipe: playbooks/recipes/core/security.yml... ✅ PASS
Checking core recipe: playbooks/recipes/core/base.yml... ✅ PASS
Checking cache recipe: playbooks/recipes/cache/redis.yml... ✅ PASS

🎉 All syntax checks passed!
```

### 🔐 test-auth.yml
**Authentication flow tester** - Validates the security setup process.

**What it tests:**
- ✅ Admin user creation
- ✅ Password and group setup
- ✅ Sudo configuration
- ✅ SSH key installation
- ✅ Firewall configuration
- ✅ SSH port setup

**Usage:**
```bash
# Dry run test (recommended)
ansible-playbook -i cloudy/inventory/test.yml dev/test-auth.yml --check

# Actual test (careful!)  
ansible-playbook -i cloudy/inventory/test.yml dev/test-auth.yml
```

## When to Use Each Tool

### Before Committing Code
```bash
./dev/validate.py    # Run full validation
```

### Quick Development Check
```bash
./dev/syntax-check.sh    # Fast syntax-only check
```

### Testing Security Setup
```bash
ansible-playbook -i cloudy/inventory/test.yml dev/test-auth.yml --check
```

### CI/CD Integration
```bash
# In your CI pipeline
./dev/validate.py && echo "✅ Validation passed"
```

## Configuration Files

- **dev/.cspell.json** - Spell checking configuration with 369 technical terms
- **dev/.ansible-lint.yml** - Ansible linting rules and standards
- **dev/.yamlint.yml** - YAML formatting and syntax rules

## Requirements

- **Python 3.8+** (for validate.py)
- **Ansible 2.9+** (for all tools)
- **PyYAML** (usually installed with Ansible)

## Troubleshooting

### "Must be run from cloudy/ directory" 
Run tools from the project root:
```bash
cd ansible-cloudy/
./dev/validate.py
```

### "No module named yaml"
Install PyYAML:
```bash
pip install PyYAML
```

### Syntax errors in recipes
Check the specific file mentioned in the error:
```bash
ansible-playbook --syntax-check cloudy/playbooks/recipes/core/security.yml
```

### Permission denied
Make sure scripts are executable:
```bash
chmod +x dev/*.py dev/*.sh
```