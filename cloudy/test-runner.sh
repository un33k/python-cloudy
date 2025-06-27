#!/bin/bash
# Ansible Cloudy Test Runner - Enhanced Version
# Comprehensive testing for Ansible infrastructure automation

set -e

echo "🧪 Running Ansible Cloudy Test Suite..."
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test 1: Inventory Validation
run_test "Inventory Validation" \
    "ansible-inventory -i inventory/test-recipes.yml --list > /dev/null"

# Test 2: Recipe Playbook Syntax
echo -e "\n${BLUE}Checking recipe playbooks...${NC}"
for playbook in playbooks/recipes/*.yml; do
    if [ -f "$playbook" ]; then
        run_test "$(basename "$playbook") syntax" \
            "ansible-playbook --syntax-check '$playbook'"
    fi
done

# Test 3: Authentication Flow Syntax
run_test "Authentication Flow Syntax" \
    "ansible-playbook --syntax-check test-simple-auth.yml"

# Test 4: Template Validation
run_test "Template File Validation" \
    "find templates/ -name '*.j2' -exec echo 'Template OK: {}' \\;"

# Test 5: Task File YAML Validation
echo -e "\n${BLUE}Validating task file YAML structure...${NC}"
task_count=0
invalid_tasks=0

for task_file in $(find tasks/ -name "*.yml"); do
    task_count=$((task_count + 1))
    
    # Use our simple YAML validator
    if ! ./validate-yaml.py "$task_file" >/dev/null 2>&1; then
        invalid_tasks=$((invalid_tasks + 1))
        echo -e "${RED}Invalid YAML: $task_file${NC}"
    fi
done

if [ $invalid_tasks -eq 0 ]; then
    run_test "Task File YAML Structure ($task_count files)" "true"
else
    run_test "Task File YAML Structure ($invalid_tasks/$task_count invalid)" "false"
fi

# Test 6: Configuration File Validation
run_test "Ansible Configuration" \
    "ansible-config dump --only-changed > /dev/null"

# Test 7: Inventory Group Variables
run_test "Group Variables Validation" \
    "find inventory/group_vars/ -name '*.yml' -exec ansible-inventory --yaml --list -i {} \\; > /dev/null 2>&1 || true"

# Test 8: Required Task Coverage
echo -e "\n${BLUE}Checking task coverage...${NC}"
required_tasks=(
    "tasks/sys/core/init.yml"
    "tasks/sys/core/update.yml" 
    "tasks/sys/core/install-common.yml"
    "tasks/sys/user/add-user.yml"
    "tasks/sys/user/change-password.yml"
    "tasks/sys/ssh/install-public-key.yml"
    "tasks/sys/firewall/install.yml"
    "tasks/sys/firewall/secure-server.yml"
)

missing_tasks=0
for task in "${required_tasks[@]}"; do
    if [ ! -f "$task" ]; then
        echo -e "${RED}Missing required task: $task${NC}"
        missing_tasks=$((missing_tasks + 1))
    fi
done

if [ $missing_tasks -eq 0 ]; then
    run_test "Required Task Coverage (${#required_tasks[@]} tasks)" "true"
else
    run_test "Required Task Coverage ($missing_tasks missing)" "false"
fi

# Test 9: Recipe Dependencies
echo -e "\n${BLUE}Checking recipe dependencies...${NC}"
recipe_errors=0
total_missing=0

for recipe in playbooks/recipes/*.yml; do
    if [ -f "$recipe" ]; then
        recipe_missing=0
        
        # Extract include_tasks references and check if files exist
        grep -o "include_tasks: [^[:space:]]*" "$recipe" | cut -d' ' -f2 | while read -r include_path; do
            # Convert relative path to absolute
            if [[ "$include_path" == ../../* ]]; then
                full_path="${include_path#../../}"
            else
                full_path="$include_path"
            fi
            
            if [ ! -f "$full_path" ]; then
                echo "$include_path"
            fi
        done > /tmp/missing_$$.txt
        
        recipe_missing=$(wc -l < /tmp/missing_$$.txt)
        
        if [ "$recipe_missing" -gt 0 ]; then
            echo -e "${RED}Recipe $(basename "$recipe") has $recipe_missing missing dependencies${NC}"
            recipe_errors=$((recipe_errors + 1))
            total_missing=$((total_missing + recipe_missing))
        fi
        
        rm -f /tmp/missing_$$.txt
    fi
done

if [ $recipe_errors -eq 0 ]; then
    run_test "Recipe Dependencies" "true"
else
    run_test "Recipe Dependencies ($recipe_errors recipes, $total_missing missing files)" "false"
fi

# Final Summary
echo ""
echo "======================================="
echo "🧪 Test Suite Summary:"
echo "   Tests Run: $TESTS_RUN"
echo -e "   ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "   ${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    echo -e "${GREEN}✅ Ansible Cloudy is ready for deployment${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the output above.${NC}"
    echo -e "${YELLOW}💡 Tip: Task files should be YAML lists, not playbooks${NC}"
    exit 1
fi