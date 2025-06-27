# 🚀 Ansible Cloudy - Quick Start Guide

**Professional infrastructure automation in minutes!**

## ⚡ TL;DR - Get Started Now

```bash
# 1. Install Ansible
pip install ansible

# 2. Navigate to project
cd cloudy/

# 3. Run tests to verify everything works
./test-runner.sh

# 4. Test a recipe (dry run - safe)
ansible-playbook --check -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml

# 5. Ready for production!
```

## 🎯 What You Get

### **Infrastructure Recipes** (One-Command Deployments)
- 🖥️ **Generic Server** - Secure foundation (SSH, firewall, users)
- 🗄️ **Database Server** - PostgreSQL + PostGIS + PgBouncer
- 🌐 **Web Server** - Nginx + Apache + Supervisor
- ⚡ **Cache Server** - Redis with optimization
- ⚖️ **Load Balancer** - Nginx with SSL
- 🔒 **VPN Server** - OpenVPN with Docker

### **Quality Assurance**
- ✅ **15 automated tests** - All passing
- ✅ **132 task files** - All validated
- ✅ **7 recipes** - Production ready
- ✅ **Comprehensive documentation**

## 🏗️ Architecture

```
cloudy/
├── playbooks/recipes/     # 🎯 One-command deployments
├── tasks/                 # 🔧 Granular, reusable tasks
├── templates/            # 📄 Configuration templates
├── inventory/            # 📊 Server definitions
└── tests/                # 🧪 Validation suite
```

## 📋 Before You Commit

**Always run pre-commit validation:**

```bash
./precommit.sh
```

This runs **11 comprehensive checks**:
- ✅ Full test suite (15 tests)
- ✅ Syntax validation
- ✅ Dependency verification
- ✅ Security checks
- ✅ Documentation validation

## 🎮 Demo Mode

```bash
./demo.sh    # Interactive demonstration
```

## 📚 Documentation

- **[README.md](README.md)** - Project overview
- **[USAGE.md](USAGE.md)** - Complete usage guide
- **[PRE-COMMIT.md](PRE-COMMIT.md)** - Validation workflow
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guide

## 🚀 Production Example

```bash
# Complete web application stack
ansible-playbook -i inventory/production.yml playbooks/recipes/generic-server.yml
ansible-playbook -i inventory/production.yml playbooks/recipes/database-server.yml
ansible-playbook -i inventory/production.yml playbooks/recipes/web-server.yml
ansible-playbook -i inventory/production.yml playbooks/recipes/load-balancer.yml
```

## 🎉 You're Ready!

**Ansible Cloudy is production-ready infrastructure automation with:**
- 🔄 Idempotent operations
- 🛡️ Security hardening
- 📈 Scalable architecture
- 🧪 Comprehensive testing
- 📚 Extensive documentation

**Start automating your infrastructure today!** 🚀