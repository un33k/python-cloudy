#!/bin/bash
# Create Missing Task Files Script
# Analyzes recipe files and creates missing task files

set -e

echo "🔍 Analyzing recipe files for missing task dependencies..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Find all include_tasks references and check if files exist
missing_files=()
created_count=0

echo -e "\n${BLUE}Checking recipe dependencies...${NC}"

for recipe in playbooks/recipes/*.yml test-*.yml; do
    if [ -f "$recipe" ]; then
        echo "Checking $recipe..."
        
        # Extract include_tasks references
        grep -o "include_tasks: [^[:space:]]*" "$recipe" | cut -d' ' -f2 | while read -r include_path; do
            # Convert relative path to absolute
            if [[ "$include_path" == ../../* ]]; then
                full_path="${include_path#../../}"
            else
                full_path="$include_path"
            fi
            
            if [ ! -f "$full_path" ]; then
                echo -e "  ${RED}❌ Missing: $full_path${NC}"
                
                # Create the missing file
                mkdir -p "$(dirname "$full_path")"
                
                # Generate task name from path
                task_name=$(basename "$full_path" .yml | sed 's/-/ /g' | sed 's/\b\w/\U&/g')
                
                cat > "$full_path" << EOF
# $task_name Task
# Auto-generated task file - please customize as needed

---
- name: $task_name
  debug:
    msg: "TODO: Implement $task_name task"
  
# TODO: Add actual task implementation here
# Example task structure:
# - name: Install package
#   package:
#     name: example-package
#     state: present

# - name: Configure service
#   template:
#     src: config.j2
#     dest: /etc/service/config
#   notify: restart service

# - name: Start and enable service
#   systemd:
#     name: service-name
#     state: started
#     enabled: true
EOF
                
                echo -e "  ${GREEN}✅ Created: $full_path${NC}"
                ((created_count++)) || true
            else
                echo -e "  ${GREEN}✅ Exists: $full_path${NC}"
            fi
        done
    fi
done

echo ""
echo "======================================="
echo -e "${BLUE}📊 Task Creation Summary:${NC}"
echo "   Created: $created_count missing task files"

if [ $created_count -gt 0 ]; then
    echo -e "\n${GREEN}🎉 Created $created_count missing task files!${NC}"
    echo -e "${YELLOW}💡 Note: These are template files - please customize them with actual implementations${NC}"
else
    echo -e "\n${GREEN}🎉 All task dependencies are satisfied!${NC}"
fi

echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Review and customize the auto-generated task files"
echo "2. Run the test suite: ./test-runner.sh"
echo "3. Test individual recipes with: ansible-playbook -i inventory/test-recipes.yml playbooks/recipes/[recipe].yml --check"