#!/usr/bin/env python3
"""
Create Missing Task Files Script
Analyzes recipe files and creates missing task files with basic structure
"""

import os
import re
import yaml
from pathlib import Path

def extract_include_tasks(file_path):
    """Extract include_tasks references from a playbook"""
    includes = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find include_tasks references
        patterns = [
            r'include_tasks:\s*([^\s\n]+)',
            r'include_tasks:\s*"([^"]+)"',
            r"include_tasks:\s*'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            includes.extend(matches)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return includes

def create_missing_task_file(task_path, task_name):
    """Create a basic task file if it doesn't exist"""
    if os.path.exists(task_path):
        return False
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(task_path), exist_ok=True)
    
    # Generate basic task content
    content = f"""# {task_name} Task
# Auto-generated task file - please customize as needed

---
- name: {task_name}
  debug:
    msg: "TODO: Implement {task_name} task"
  
# TODO: Add actual task implementation here
# Example task structure:
# - name: Install package
#   package:
#     name: example-package
#     state: present
"""
    
    with open(task_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created: {task_path}")
    return True

def main():
    """Main function"""
    print("🔍 Analyzing recipe files for missing task dependencies...")
    
    # Find all recipe files
    recipe_files = []
    for root, dirs, files in os.walk("playbooks/recipes"):
        for file in files:
            if file.endswith('.yml'):
                recipe_files.append(os.path.join(root, file))
    
    # Also check test files
    for file in os.listdir('.'):
        if file.startswith('test-') and file.endswith('.yml'):
            recipe_files.append(file)
    
    all_includes = set()
    missing_files = []
    
    # Extract all include_tasks references
    for recipe_file in recipe_files:
        includes = extract_include_tasks(recipe_file)
        for include in includes:
            # Convert relative path to absolute
            if include.startswith('../../'):
                full_path = include.replace('../../', '')
            else:
                full_path = include
            
            all_includes.add(full_path)
            
            if not os.path.exists(full_path):
                missing_files.append((full_path, recipe_file))
    
    print(f"📊 Found {len(all_includes)} task references across {len(recipe_files)} recipe files")
    print(f"❌ Missing: {len(missing_files)} task files")
    
    if not missing_files:
        print("🎉 All task dependencies are satisfied!")
        return
    
    print("\n📝 Creating missing task files...")
    created_count = 0
    
    for task_path, source_recipe in missing_files:
        # Generate task name from path
        task_name = os.path.basename(task_path).replace('.yml', '').replace('-', ' ').title()
        
        if create_missing_task_file(task_path, task_name):
            created_count += 1
    
    print(f"\n🎉 Created {created_count} missing task files!")
    print("💡 Note: These are template files - please customize them with actual implementations")
    
    # Show remaining missing files (if any)
    still_missing = [path for path, _ in missing_files if not os.path.exists(path)]
    if still_missing:
        print(f"\n⚠️  Still missing {len(still_missing)} files:")
        for path in still_missing:
            print(f"   - {path}")

if __name__ == "__main__":
    main()