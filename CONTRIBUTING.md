# Contributing to Ansible Cloudy

Welcome to Ansible Cloudy! This guide will help you contribute effectively to this infrastructure automation project.

## 🚀 Quick Start for Contributors

### Prerequisites

```bash
# Install required tools
pip install ansible ansible-lint yamllint

# Clone and navigate to project
git clone <repository-url>
cd ansible-cloudy/cloudy/
```

### Development Workflow

1. **Run Tests**: Always run the test suite before making changes
   ```bash
   ./test-runner.sh
   ```

2. **Make Changes**: Follow the project structure and conventions

3. **Validate Changes**: Run tests and linting
   ```bash
   ./test-runner.sh
   yamllint -d relaxed .
   ansible-lint playbooks/recipes/
   ```

4. **Test Recipes**: Test your changes in check mode
   ```bash
   ansible-playbook --check -i inventory/test-recipes.yml playbooks/recipes/your-recipe.yml
   ```

## 📁 Project Structure

```
cloudy/
├── playbooks/recipes/     # High-level deployment recipes
├── tasks/                 # Granular, reusable tasks
│   ├── sys/              # System operations
│   ├── db/               # Database management
│   ├── web/              # Web server configuration
│   └── services/         # Service management
├── templates/            # Jinja2 configuration templates
├── inventory/            # Server inventory files
├── tests/                # Test files and validation
└── scripts/              # Utility scripts
```

## 🎯 Contribution Guidelines

### Task Files

**✅ DO:**
- Create one task per file with a single responsibility
- Use descriptive task names that explain the purpose
- Include proper error handling and validation
- Add debug messages for important operations
- Follow YAML best practices

**❌ DON'T:**
- Create monolithic task files with multiple responsibilities
- Use hardcoded values without variables
- Skip error handling for critical operations
- Use deprecated Ansible modules

**Example Task Structure:**
```yaml
---
- name: Install and configure Nginx web server
  package:
    name: nginx
    state: present
  register: nginx_install
  
- name: Start and enable Nginx service
  systemd:
    name: nginx
    state: started
    enabled: true
  when: nginx_install is succeeded
  
- name: Display installation status
  debug:
    msg: "✅ Nginx installed and configured successfully"
```

### Recipe Files

**✅ DO:**
- Compose recipes from existing tasks when possible
- Include comprehensive pre_tasks and post_tasks sections
- Use meaningful variable names and defaults
- Provide clear documentation in comments
- Include tags for selective execution

**❌ DON'T:**
- Duplicate task logic in recipes
- Use deprecated `include` statements (use `include_tasks`)
- Skip variable validation
- Create recipes without proper error handling

**Example Recipe Structure:**
```yaml
---
- name: Example Server Setup Recipe
  hosts: example_servers
  gather_facts: true
  become: true
  
  vars:
    setup_firewall: true
    setup_ssl: false
    
  pre_tasks:
    - name: Display setup information
      debug:
        msg: |
          🚀 Starting Example Server Setup
          Target: {{ inventory_hostname }}
          
  tasks:
    - name: Include foundation tasks
      include_tasks: ../../tasks/sys/core/init.yml
      tags: [foundation]
      
  post_tasks:
    - name: Display completion summary
      debug:
        msg: "🎉 ✅ Example server setup completed!"
```

### Inventory Configuration

**✅ DO:**
- Use descriptive group names
- Provide sensible defaults in group_vars
- Document required variables
- Use consistent naming conventions

**Example Inventory:**
```yaml
all:
  vars:
    ansible_user: admin
    ansible_port: 22022
    
  children:
    web_servers:
      hosts:
        web1:
          ansible_host: 10.0.1.10
          domain_name: app.example.com
```

## 🧪 Testing

### Running Tests

```bash
# Full test suite
./test-runner.sh

# Individual validations
./validate-yaml.py tasks/sys/core/init.yml
ansible-playbook --syntax-check playbooks/recipes/web-server.yml
ansible-inventory -i inventory/test-recipes.yml --list
```

### Test Categories

1. **Syntax Validation**: YAML and Ansible syntax checks
2. **Dependency Validation**: Ensure all included tasks exist
3. **Structure Validation**: Verify proper file organization
4. **Inventory Validation**: Check inventory configuration
5. **Template Validation**: Validate Jinja2 templates

### Adding New Tests

When adding new functionality:

1. Add test cases to `test-runner.sh`
2. Update `create-missing-tasks.sh` if adding new dependencies
3. Include example usage in documentation
4. Test in check mode before implementation

## 🔧 Development Tools

### Useful Scripts

- `./test-runner.sh` - Comprehensive test suite
- `./create-missing-tasks.sh` - Create missing task dependencies
- `./validate-yaml.py` - YAML structure validation

### IDE Configuration

**VS Code Extensions:**
- Ansible (Red Hat)
- YAML (Red Hat)
- Jinja (wholroyd)

**Settings:**
```json
{
  "ansible.python.interpreterPath": "/usr/bin/python3",
  "yaml.schemas": {
    "https://raw.githubusercontent.com/ansible/ansible/devel/lib/ansible/modules/": "*.yml"
  }
}
```

## 📝 Documentation Standards

### Task Documentation

```yaml
# Task Purpose and Context
# Based on: original-implementation-reference (if applicable)
# Usage: include_tasks: path/to/task.yml

---
- name: Clear, descriptive task name
  module:
    parameter: value
```

### Recipe Documentation

```yaml
# Recipe: Purpose and Scope
# Based on: original-implementation-reference (if applicable)
# Usage: ansible-playbook -i inventory.yml recipe.yml

---
- name: Descriptive Recipe Name
  hosts: target_group
```

## 🚦 Code Review Process

### Before Submitting

1. ✅ All tests pass (`./test-runner.sh`)
2. ✅ Code follows project conventions
3. ✅ Documentation is updated
4. ✅ No hardcoded values or secrets
5. ✅ Error handling is implemented

### Review Checklist

- [ ] Task files follow single responsibility principle
- [ ] Recipes compose existing tasks appropriately
- [ ] Variables are properly defined and documented
- [ ] Error handling covers failure scenarios
- [ ] Tests validate the new functionality
- [ ] Documentation explains usage and purpose

## 🐛 Troubleshooting

### Common Issues

**Syntax Errors:**
```bash
# Check YAML syntax
./validate-yaml.py path/to/file.yml

# Check Ansible syntax
ansible-playbook --syntax-check playbook.yml
```

**Missing Dependencies:**
```bash
# Auto-create missing task files
./create-missing-tasks.sh
```

**Inventory Issues:**
```bash
# Validate inventory
ansible-inventory -i inventory/file.yml --list
```

### Getting Help

1. Check existing documentation in `USAGE.md` and `CLAUDE.md`
2. Run the test suite to identify specific issues
3. Review similar implementations in the codebase
4. Open an issue with detailed error information

## 🎉 Recognition

Contributors who follow these guidelines and make meaningful improvements will be recognized in:

- Project README
- Release notes
- Contributor documentation

Thank you for helping make Ansible Cloudy an amazing infrastructure automation tool! 🚀