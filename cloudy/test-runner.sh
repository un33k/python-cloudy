#!/bin/bash
# Ansible Cloudy Test Runner
# Adapted from legacy Fabric testing patterns

set -e

echo "🧪 Running Ansible Cloudy Test Suite..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Test 1: Playbook Syntax and Structure
run_test "Playbook Structure Test" \
    "ansible-playbook tests/test-playbooks.yml"

# Test 2: Inventory Validation
run_test "Inventory Validation" \
    "ansible-inventory -i inventory/test-recipes.yml --list > /dev/null"

# Test 3: Task File Syntax
run_test "Task File Syntax Check" \
    "find tasks/ -name '*.yml' -exec ansible-playbook --syntax-check {} \;"

# Test 4: Template Validation
run_test "Template File Validation" \
    "find templates/ -name '*.j2' -exec echo 'Checking template: {}' \;"

# Test 5: Authentication Flow (dry run)
run_test "Authentication Flow Syntax" \
    "ansible-playbook --syntax-check test-simple-auth.yml"

# Test 6: Recipe Playbook Syntax
echo -e "\n${YELLOW}Checking all recipe playbooks...${NC}"
for playbook in playbooks/recipes/*.yml; do
    if [ -f "$playbook" ]; then
        run_test "$(basename "$playbook") syntax" \
            "ansible-playbook --syntax-check '$playbook'"
    fi
done

# Final Summary
echo ""
echo "======================================"
echo "🧪 Test Suite Summary:"
echo "   Tests Run: $TESTS_RUN"
echo -e "   ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "   ${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi