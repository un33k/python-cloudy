#!/bin/bash
# Pre-commit validation script for Ansible Cloudy
# Run this before committing to ensure code quality and prevent issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Counters
CHECKS_RUN=0
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

echo -e "${BLUE}"
cat << "EOF"
 ____                                     _ _   
|  _ \ _ __ ___        ___ ___  _ __ ___  | | |_ 
| |_) | '__/ _ \_____ / __/ _ \| '_ ` _ \ | | __|
|  __/| | |  __/_____| (_| (_) | | | | | | | |_ 
|_|   |_|  \___|      \___\___/|_| |_| |_|_|\__|
                                                
EOF
echo -e "${NC}"

echo -e "${BLUE}🔍 Running Pre-commit Validation for Ansible Cloudy${NC}"
echo -e "${BLUE}===================================================${NC}"
echo ""

# Function to run checks
run_check() {
    local check_name="$1"
    local check_command="$2"
    local is_warning="${3:-false}"
    
    echo -e "${YELLOW}🔍 $check_name${NC}"
    CHECKS_RUN=$((CHECKS_RUN + 1))
    
    if eval "$check_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED: $check_name${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        if [ "$is_warning" = "true" ]; then
            echo -e "${YELLOW}⚠️  WARNING: $check_name${NC}"
            WARNINGS=$((WARNINGS + 1))
            return 0
        else
            echo -e "${RED}❌ FAILED: $check_name${NC}"
            CHECKS_FAILED=$((CHECKS_FAILED + 1))
            return 1
        fi
    fi
}

# Function to run checks with output
run_check_with_output() {
    local check_name="$1"
    local check_command="$2"
    
    echo -e "${YELLOW}🔍 $check_name${NC}"
    CHECKS_RUN=$((CHECKS_RUN + 1))
    
    if eval "$check_command"; then
        echo -e "${GREEN}✅ PASSED: $check_name${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED: $check_name${NC}"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
        return 1
    fi
}

echo -e "${PURPLE}Phase 1: Core Validation${NC}"
echo "========================"

# Check 1: Comprehensive Test Suite
run_check_with_output "Comprehensive Test Suite" "./test-runner.sh"

echo -e "\n${PURPLE}Phase 2: Code Quality Checks${NC}"
echo "============================="

# Check 2: YAML Linting (if yamllint is available)
if command -v yamllint >/dev/null 2>&1; then
    run_check "YAML Linting" "yamllint -d relaxed playbooks/ inventory/ templates/ tasks/" "true"
else
    echo -e "${YELLOW}⚠️  SKIPPED: YAML Linting (yamllint not installed)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check 3: Ansible Linting (if ansible-lint is available)
if command -v ansible-lint >/dev/null 2>&1; then
    run_check "Ansible Linting" "ansible-lint playbooks/recipes/" "true"
else
    echo -e "${YELLOW}⚠️  SKIPPED: Ansible Linting (ansible-lint not installed)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

echo -e "\n${PURPLE}Phase 3: Syntax Validation${NC}"
echo "=========================="

# Check 4: Individual Recipe Syntax
echo -e "${YELLOW}🔍 Recipe Syntax Validation${NC}"
recipe_errors=0
for recipe in playbooks/recipes/*.yml; do
    if [ -f "$recipe" ]; then
        if ansible-playbook --syntax-check "$recipe" >/dev/null 2>&1; then
            echo -e "   ✅ $(basename "$recipe")"
        else
            echo -e "   ${RED}❌ $(basename "$recipe")${NC}"
            recipe_errors=$((recipe_errors + 1))
        fi
    fi
done

if [ $recipe_errors -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: Recipe Syntax Validation${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}❌ FAILED: Recipe Syntax Validation ($recipe_errors errors)${NC}"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi
CHECKS_RUN=$((CHECKS_RUN + 1))

echo -e "\n${PURPLE}Phase 4: Dependency Validation${NC}"
echo "==============================="

# Check 5: Task Dependencies
run_check "Task Dependencies" "./create-missing-tasks.sh | grep -q 'All task dependencies are satisfied'"

# Check 6: YAML Structure
run_check "YAML Structure Validation" "find tasks/ -name '*.yml' -exec ./validate-yaml.py {} \\;"

echo -e "\n${PURPLE}Phase 5: Configuration Validation${NC}"
echo "=================================="

# Check 7: Inventory Validation
run_check "Inventory Configuration" "ansible-inventory -i inventory/test-recipes.yml --list"

# Check 8: Ansible Configuration
run_check "Ansible Configuration" "ansible-config dump --only-changed"

echo -e "\n${PURPLE}Phase 6: Security Checks${NC}"
echo "========================"

# Check 9: No Hardcoded Secrets
echo -e "${YELLOW}🔍 Security: Hardcoded Secrets Check${NC}"
# Look for actual hardcoded passwords (not variable references or comments)
if grep -r "password:[[:space:]]*['\"][^{].*['\"]" playbooks/ tasks/ --include="*.yml" | grep -v "#" >/dev/null 2>&1; then
    echo -e "${RED}❌ FAILED: Found potential hardcoded secrets${NC}"
    echo -e "${YELLOW}   Review these findings:${NC}"
    grep -r "password:[[:space:]]*['\"][^{].*['\"]" playbooks/ tasks/ --include="*.yml" | grep -v "#" | head -5
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
else
    echo -e "${GREEN}✅ PASSED: No hardcoded secrets found${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi
CHECKS_RUN=$((CHECKS_RUN + 1))

# Check 10: No Debug Tasks in Production
echo -e "${YELLOW}🔍 Security: Debug Tasks Check${NC}"
debug_count=$(grep -r "debug:" tasks/ playbooks/ --include="*.yml" | wc -l)
if [ "$debug_count" -gt 50 ]; then
    echo -e "${YELLOW}⚠️  WARNING: High number of debug tasks ($debug_count) - review for production${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ PASSED: Reasonable number of debug tasks ($debug_count)${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi
CHECKS_RUN=$((CHECKS_RUN + 1))

echo -e "\n${PURPLE}Phase 7: Documentation Checks${NC}"
echo "=============================="

# Check 11: Documentation Files Present
echo -e "${YELLOW}🔍 Documentation Completeness${NC}"
required_docs=("README.md" "USAGE.md" "CLAUDE.md" "CONTRIBUTING.md" "cloudy/DEVELOPMENT.md")
missing_docs=0

for doc in "${required_docs[@]}"; do
    if [ -f "../$doc" ] || [ -f "$doc" ]; then
        echo -e "   ✅ $doc"
    else
        echo -e "   ${RED}❌ $doc (missing)${NC}"
        missing_docs=$((missing_docs + 1))
    fi
done

if [ $missing_docs -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: All required documentation present${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}❌ FAILED: Missing $missing_docs documentation files${NC}"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi
CHECKS_RUN=$((CHECKS_RUN + 1))

echo -e "\n${PURPLE}Phase 8: Git Checks${NC}"
echo "==================="

# Check 12: Git Status
echo -e "${YELLOW}🔍 Git Status Check${NC}"
if git status --porcelain | grep -q .; then
    echo -e "${GREEN}✅ PASSED: Changes detected and ready for commit${NC}"
    echo -e "${BLUE}   Modified files:${NC}"
    git status --porcelain | head -10
    if [ "$(git status --porcelain | wc -l)" -gt 10 ]; then
        echo -e "${BLUE}   ... and $(($(git status --porcelain | wc -l) - 10)) more files${NC}"
    fi
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${YELLOW}⚠️  WARNING: No changes detected${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
CHECKS_RUN=$((CHECKS_RUN + 1))

# Check 13: Large Files Check
echo -e "${YELLOW}🔍 Large Files Check${NC}"
large_files=$(find . -type f -size +1M -not -path "./.git/*" 2>/dev/null | wc -l)
if [ "$large_files" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Found $large_files large files (>1MB)${NC}"
    find . -type f -size +1M -not -path "./.git/*" 2>/dev/null | head -5
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✅ PASSED: No large files detected${NC}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
fi
CHECKS_RUN=$((CHECKS_RUN + 1))

# Final Summary
echo ""
echo "=============================================="
echo -e "${BLUE}🔍 Pre-commit Validation Summary${NC}"
echo "=============================================="
echo "   Checks Run: $CHECKS_RUN"
echo -e "   ${GREEN}Passed: $CHECKS_PASSED${NC}"
echo -e "   ${RED}Failed: $CHECKS_FAILED${NC}"
echo -e "   ${YELLOW}Warnings: $WARNINGS${NC}"

# Recommendations
echo ""
echo -e "${BLUE}📋 Recommendations:${NC}"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed - READY TO COMMIT!${NC}"
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Consider addressing $WARNINGS warnings before commit${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🚀 Suggested commit workflow:${NC}"
    echo -e "   1. ${CYAN}git add .${NC}"
    echo -e "   2. ${CYAN}git commit -m \"Your commit message\"${NC}"
    echo -e "   3. ${CYAN}git push${NC}"
    
    if command -v ansible-lint >/dev/null 2>&1 && command -v yamllint >/dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}💡 All linting tools available - excellent code quality!${NC}"
    else
        echo ""
        echo -e "${YELLOW}💡 Install additional tools for better validation:${NC}"
        if ! command -v yamllint >/dev/null 2>&1; then
            echo -e "   ${CYAN}pip install yamllint${NC}"
        fi
        if ! command -v ansible-lint >/dev/null 2>&1; then
            echo -e "   ${CYAN}pip install ansible-lint${NC}"
        fi
    fi
    
    exit 0
else
    echo -e "${RED}❌ $CHECKS_FAILED critical checks failed - DO NOT COMMIT YET${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Fix the following before committing:${NC}"
    echo -e "   1. Run ${CYAN}./test-runner.sh${NC} and fix any failures"
    echo -e "   2. Check syntax errors in recipes"
    echo -e "   3. Resolve dependency issues"
    echo -e "   4. Review security warnings"
    echo ""
    echo -e "${BLUE}💡 After fixes, run this script again: ${CYAN}./precommit.sh${NC}"
    
    exit 1
fi