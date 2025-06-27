#!/bin/bash
# Quick Ansible Syntax Checker
# Fast syntax validation for all playbooks and recipes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Quick Ansible Syntax Check${NC}"
echo "==============================="

# Check if we're in the right directory
if [ ! -f "cloudy/ansible.cfg" ]; then
    echo -e "${RED}❌ Must be run from the project root directory (ansible-cloudy/)${NC}"
    exit 1
fi

# Counters
TOTAL=0
PASSED=0
FAILED=0

# Function to check syntax
check_syntax() {
    local file="$1"
    local type="$2"
    
    echo -n -e "${YELLOW}Checking $type: $file...${NC} "
    TOTAL=$((TOTAL + 1))
    
    if ansible-playbook --syntax-check "$file" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED=$((FAILED + 1))
        # Show the error
        echo -e "${RED}Error details:${NC}"
        ansible-playbook --syntax-check "$file" 2>&1 | sed 's/^/  /'
        echo ""
    fi
}

echo -e "\n${BLUE}Checking core recipes...${NC}"
if [ -d "cloudy/playbooks/recipes/core" ]; then
    for recipe in cloudy/playbooks/recipes/core/*.yml; do
        if [ -f "$recipe" ]; then
            check_syntax "$recipe" "core recipe"
        fi
    done
else
    echo -e "${YELLOW}⚠️  No core recipes found${NC}"
fi

echo -e "\n${BLUE}Checking service recipes...${NC}"
for category in cache db lb vpn www; do
    if [ -d "cloudy/playbooks/recipes/$category" ]; then
        for recipe in cloudy/playbooks/recipes/$category/*.yml; do
            if [ -f "$recipe" ]; then
                check_syntax "$recipe" "$category recipe"
            fi
        done
    fi
done

echo -e "\n${BLUE}Checking dev files...${NC}"
if [ -d "dev" ]; then
    for dev_file in dev/*.yml; do
        if [ -f "$dev_file" ]; then
            check_syntax "$dev_file" "dev file"
        fi
    done
fi

# Summary
echo ""
echo "==============================="
echo -e "${BLUE}📊 Syntax Check Summary:${NC}"
echo -e "   Total files: $TOTAL"
echo -e "   ${GREEN}Passed: $PASSED${NC}"
echo -e "   ${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All syntax checks passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ $FAILED syntax errors found${NC}"
    exit 1
fi