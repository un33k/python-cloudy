#!/bin/bash
# Ansible Cloudy Demo Script
# Demonstrates the capabilities of the infrastructure automation system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << "EOF"
   ___              _ _     _        _____ _                 _       
  / _ \            (_) |   | |      /  ___| |               | |      
 / /_\ \_ __  ___  _| |__ | | ___  \ `--.| | ___  _   _  __| |_   _ 
 |  _  | '_ \/ __|| | '_ \| |/ _ \  `--. \ |/ _ \| | | |/ _` | | | |
 | | | | | | \__ \| | |_) | |  __/ /\__/ / | (_) | |_| | (_| | |_| |
 \_| |_/_| |_|___/|_|_.__/|_|\___| \____/|_|\___/ \__,_|\__,_|\__, |
                                                              __/ |
                                                             |___/ 
EOF
echo -e "${NC}"

echo -e "${BLUE}🚀 Welcome to Ansible Cloudy - Infrastructure Automation Demo${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Function to run demo steps
demo_step() {
    local step_num="$1"
    local step_name="$2"
    local step_desc="$3"
    
    echo -e "\n${YELLOW}📋 Step $step_num: $step_name${NC}"
    echo -e "${CYAN}$step_desc${NC}"
    echo ""
    read -p "Press Enter to continue..."
}

# Function to run commands with explanation
run_command() {
    local cmd="$1"
    local desc="$2"
    
    echo -e "${GREEN}💻 Running: ${NC}$cmd"
    if [ -n "$desc" ]; then
        echo -e "${PURPLE}   → $desc${NC}"
    fi
    echo ""
    
    eval "$cmd"
    echo ""
}

# Demo Steps
demo_step "1" "Project Overview" \
    "Ansible Cloudy provides infrastructure automation with granular tasks and composable recipes."

run_command "ls -la" \
    "Show project structure"

run_command "find playbooks/recipes/ -name '*.yml' | head -10" \
    "Available deployment recipes"

run_command "find tasks/ -type d | head -10" \
    "Granular task organization"

demo_step "2" "Test Suite Validation" \
    "Run comprehensive tests to validate all components"

run_command "./test-runner.sh" \
    "Execute full test suite with syntax validation, dependency checks, and structure validation"

demo_step "3" "Recipe Syntax Validation" \
    "Validate individual recipe playbooks"

run_command "ansible-playbook --syntax-check playbooks/recipes/generic-server.yml" \
    "Check generic server recipe syntax"

run_command "ansible-playbook --syntax-check playbooks/recipes/web-server.yml" \
    "Check web server recipe syntax"

run_command "ansible-playbook --syntax-check playbooks/recipes/database-server.yml" \
    "Check database server recipe syntax"

demo_step "4" "Inventory Configuration" \
    "Examine server inventory and configuration"

run_command "ansible-inventory -i inventory/test-recipes.yml --list" \
    "Display parsed inventory configuration"

run_command "cat inventory/test-recipes.yml" \
    "Show inventory file structure"

demo_step "5" "Task Dependencies" \
    "Verify all task dependencies are satisfied"

run_command "./create-missing-tasks.sh" \
    "Check and create any missing task dependencies"

demo_step "6" "Dry Run Examples" \
    "Demonstrate recipe execution in check mode (safe, no changes)"

echo -e "${YELLOW}⚠️  Note: These are dry runs (--check mode) - no actual changes will be made${NC}"
echo ""

run_command "ansible-playbook --check -i inventory/test-recipes.yml playbooks/recipes/generic-server.yml" \
    "Dry run: Generic server setup (foundation)"

run_command "ansible-playbook --check -i inventory/test-recipes.yml playbooks/recipes/cache-server.yml" \
    "Dry run: Redis cache server setup"

demo_step "7" "Template and Configuration Files" \
    "Show configuration templates and their usage"

run_command "ls -la templates/" \
    "Available configuration templates"

run_command "head -20 templates/nginx.conf.j2" \
    "Example Nginx configuration template"

demo_step "8" "Documentation and Usage" \
    "Review comprehensive documentation"

echo -e "${GREEN}📚 Available Documentation:${NC}"
echo -e "   • ${CYAN}README.md${NC} - Project overview and quick start"
echo -e "   • ${CYAN}USAGE.md${NC} - Complete usage guide with examples"
echo -e "   • ${CYAN}CLAUDE.md${NC} - Developer reference and commands"
echo -e "   • ${CYAN}CONTRIBUTING.md${NC} - Contribution guidelines"
echo -e "   • ${CYAN}cloudy/DEVELOPMENT.md${NC} - Technical implementation details"
echo ""

run_command "head -30 USAGE.md" \
    "Preview usage documentation"

demo_step "9" "Recipe Categories" \
    "Overview of available infrastructure recipes"

echo -e "${GREEN}🏗️  Available Infrastructure Recipes:${NC}"
echo ""
echo -e "   ${CYAN}🖥️  Generic Server${NC}     - Foundation setup (SSH, firewall, users)"
echo -e "   ${CYAN}🗄️  Database Server${NC}    - PostgreSQL + PostGIS + PgBouncer"
echo -e "   ${CYAN}🌐 Web Server${NC}         - Nginx + Apache + Supervisor"
echo -e "   ${CYAN}⚡ Cache Server${NC}       - Redis with memory optimization"
echo -e "   ${CYAN}⚖️  Load Balancer${NC}     - Nginx load balancer with SSL"
echo -e "   ${CYAN}🔒 VPN Server${NC}         - OpenVPN with Docker"
echo ""

demo_step "10" "Production Usage Examples" \
    "Real-world deployment scenarios"

echo -e "${GREEN}🚀 Production Deployment Examples:${NC}"
echo ""
echo -e "${YELLOW}Complete Web Application Stack:${NC}"
echo -e "   1. ${CYAN}ansible-playbook -i inventory/production.yml playbooks/recipes/generic-server.yml${NC}"
echo -e "   2. ${CYAN}ansible-playbook -i inventory/production.yml playbooks/recipes/database-server.yml${NC}"
echo -e "   3. ${CYAN}ansible-playbook -i inventory/production.yml playbooks/recipes/web-server.yml${NC}"
echo -e "   4. ${CYAN}ansible-playbook -i inventory/production.yml playbooks/recipes/load-balancer.yml${NC}"
echo ""
echo -e "${YELLOW}Single-Purpose Servers:${NC}"
echo -e "   • ${CYAN}VPN Server:${NC} ansible-playbook -i inventory/vpn.yml playbooks/recipes/vpn-server.yml"
echo -e "   • ${CYAN}Cache Server:${NC} ansible-playbook -i inventory/cache.yml playbooks/recipes/cache-server.yml"
echo ""

echo -e "\n${GREEN}🎉 Demo Complete!${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${CYAN}Ansible Cloudy is ready for infrastructure automation!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "   1. Configure your inventory files with real server details"
echo -e "   2. Customize variables for your environment"
echo -e "   3. Run recipes against your infrastructure"
echo -e "   4. Monitor and maintain your automated infrastructure"
echo ""
echo -e "${GREEN}📖 For detailed usage instructions, see USAGE.md${NC}"
echo -e "${GREEN}🔧 For development guidelines, see CONTRIBUTING.md${NC}"
echo ""