#!/usr/bin/env python3
"""
Simple YAML validation script that doesn't require external dependencies
"""

import sys
import os

def validate_yaml_basic(filepath):
    """Basic YAML validation without external dependencies"""
    try:
        with open(filepath, 'r') as f:
            content = f.read().strip()
        
        # Basic checks
        if not content:
            return False, "Empty file"
        
        if '---' not in content:
            return False, "Missing YAML document start marker (---)"
        
        # Check for basic YAML structure issues
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                # Check for basic indentation issues
                if line.startswith(' ') and not line.startswith('  '):
                    # Single space indentation is usually wrong
                    if not line.startswith(' -') and not line.startswith(' #'):
                        return False, f"Line {i}: Possible indentation issue"
        
        return True, "Valid YAML structure"
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: validate-yaml.py <file.yml>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    is_valid, message = validate_yaml_basic(filepath)
    
    if is_valid:
        print(f"✅ {filepath}: {message}")
        sys.exit(0)
    else:
        print(f"❌ {filepath}: {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()