# Pre-commit Validation Guide

This guide shows you exactly what to run before committing code to ensure quality and prevent issues.

## 🚀 Quick Commands (TL;DR)

```bash
# Navigate to cloudy directory
cd cloudy/

# Run comprehensive pre-commit validation
./precommit.sh

# If all checks pass, commit your changes
git add .
git commit -m "Your commit message"
git push
```

## 🔧 Detailed Pre-commit Workflow

### 1. **Comprehensive Validation** (Required)
```bash
./precommit.sh
```
This runs **13 different checks** including:
- ✅ Full test suite (15 tests)
- ✅ YAML and Ansible linting
- ✅ Syntax validation for all recipes
- ✅ Dependency verification
- ✅ Security checks
- ✅ Documentation completeness

### 2. **Individual Check Commands** (Optional)

If you want to run specific checks manually:

```bash
# Core test suite
./test-runner.sh

# YAML validation
yamllint -d relaxed playbooks/ inventory/ templates/ tasks/

# Ansible linting
ansible-lint playbooks/recipes/

# Syntax check individual recipe
ansible-playbook --syntax-check playbooks/recipes/generic-server.yml

# Dependency verification
./create-missing-tasks.sh

# YAML structure validation
./validate-yaml.py tasks/sys/core/init.yml

# Inventory validation
ansible-inventory -i inventory/test-recipes.yml --list
```

## 🎯 Automated Git Hooks

### Install Automatic Pre-commit Hook
```bash
# Install Git hook (one-time setup)
./install-git-hooks.sh
```

After installation:
- ✅ **Every `git commit` automatically runs validation**
- ✅ **Commits are blocked if validation fails**
- ✅ **No more broken commits in the repository**

### Manual Git Workflow (without hooks)
```bash
# 1. Run validation
./precommit.sh

# 2. If validation passes, commit
git add .
git commit -m "feat: add new database recipe with PostGIS support"
git push
```

## 📊 What Gets Validated

### **Phase 1: Core Validation**
- 🧪 **Comprehensive Test Suite** - All 15 tests must pass

### **Phase 2: Code Quality**
- 📝 **YAML Linting** - Consistent formatting and structure
- 🔧 **Ansible Linting** - Best practices and conventions

### **Phase 3: Syntax Validation**
- ✅ **Recipe Syntax** - All 7 playbooks must be valid
- ✅ **Task Structure** - All 132 task files validated

### **Phase 4: Dependencies**
- 🔗 **Task Dependencies** - All includes must exist
- 📋 **YAML Structure** - Proper document format

### **Phase 5: Configuration**
- 📊 **Inventory** - Server configurations valid
- ⚙️ **Ansible Config** - Core settings verified

### **Phase 6: Security**
- 🔒 **No Hardcoded Secrets** - Prevents credential leaks
- 🐛 **Debug Task Review** - Production readiness check

### **Phase 7: Documentation**
- 📚 **Required Docs** - All documentation files present
- 📖 **Completeness** - README, USAGE, CONTRIBUTING guides

### **Phase 8: Git Checks**
- 📁 **File Changes** - Confirms changes ready for commit
- 📦 **Large Files** - Prevents repository bloat

## 🚨 Common Issues & Solutions

### ❌ Test Suite Failures
```bash
# Run individual test to identify issue
./test-runner.sh

# Check specific recipe syntax
ansible-playbook --syntax-check playbooks/recipes/problematic-recipe.yml
```

### ❌ YAML Linting Errors
```bash
# Fix YAML formatting
yamllint -d relaxed playbooks/recipes/your-file.yml

# Common fixes:
# - Fix indentation (use 2 spaces)
# - Remove trailing spaces
# - Add document start marker (---)
```

### ❌ Dependency Issues
```bash
# Auto-create missing task files
./create-missing-tasks.sh

# Manually check specific dependency
ls -la tasks/path/to/missing-task.yml
```

### ❌ Security Warnings
```bash
# Review potential hardcoded secrets
grep -r "password.*=" playbooks/ tasks/ --include="*.yml"

# Use variables instead:
# Bad:  password: "hardcoded123"
# Good: password: "{{ admin_password }}"
```

## 🎉 Success Indicators

When `./precommit.sh` completes successfully, you'll see:

```
✅ All critical checks passed - READY TO COMMIT!

🚀 Suggested commit workflow:
   1. git add .
   2. git commit -m "Your commit message"
   3. git push
```

## 🛠️ Tool Installation

### Required Tools (Core)
```bash
pip install ansible
```

### Optional Tools (Enhanced Validation)
```bash
pip install yamllint ansible-lint
```

### Verification
```bash
# Check tool availability
ansible --version
yamllint --version  # optional
ansible-lint --version  # optional
```

## 📋 Commit Message Guidelines

Use conventional commit format:

```bash
# Feature additions
git commit -m "feat: add Redis cache server recipe"

# Bug fixes
git commit -m "fix: resolve SSH key installation issue"

# Documentation updates
git commit -m "docs: update usage guide with examples"

# Tests
git commit -m "test: add validation for template files"

# Refactoring
git commit -m "refactor: improve task file organization"
```

## 🔄 Bypass Pre-commit (Emergency Only)

```bash
# Skip validation (NOT RECOMMENDED)
git commit --no-verify -m "emergency fix"

# Better approach: Fix issues first
./precommit.sh  # identify issues
# fix issues
./precommit.sh  # verify fixes
git commit -m "proper fix with validation"
```

---

**Remember: The pre-commit validation ensures that Ansible Cloudy maintains its high quality standards and prevents broken deployments!** 🚀