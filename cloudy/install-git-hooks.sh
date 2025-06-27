#!/bin/bash
# Install Git pre-commit hooks for Ansible Cloudy

echo "🔧 Installing Git pre-commit hooks for Ansible Cloudy..."

# Check if we're in a git repository
if [ ! -d "../.git" ]; then
    echo "❌ Error: Not in a Git repository root"
    echo "   Run this from the cloudy/ directory of your Git repository"
    exit 1
fi

# Create pre-commit hook
cat > ../.git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Git pre-commit hook for Ansible Cloudy
# Automatically runs validation before commits

echo "🔍 Running pre-commit validation..."

# Change to cloudy directory
cd cloudy/ || exit 1

# Run pre-commit validation
if ./precommit.sh; then
    echo "✅ Pre-commit validation passed"
    exit 0
else
    echo "❌ Pre-commit validation failed"
    echo "   Fix issues and try committing again"
    exit 1
fi
EOF

# Make hook executable
chmod +x ../.git/hooks/pre-commit

echo "✅ Git pre-commit hook installed successfully!"
echo ""
echo "📋 What happens now:"
echo "   • Every 'git commit' will automatically run validation"
echo "   • Commits will be blocked if validation fails"
echo "   • You can bypass with 'git commit --no-verify' (not recommended)"
echo ""
echo "🧪 Test the hook:"
echo "   cd cloudy/ && ./precommit.sh"