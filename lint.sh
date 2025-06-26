#!/bin/bash

# Python Cloudy Linting Script
# Runs multiple linting tools to ensure code quality

set -e

echo "🔍 Running Python Cloudy linting checks..."
echo "=========================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider running:"
    echo "   source .venv/bin/activate"
    echo ""
fi

# Install linting tools if not present
echo "📦 Ensuring linting tools are installed..."
pip install -q black flake8 isort mypy 2>/dev/null || true

# Run Black formatter (100 character line length)
echo ""
echo "🖤 Running Black formatter..."
black --line-length 100 --check --diff cloudy/ || {
    echo "❌ Black formatting issues found. Run 'black --line-length 100 cloudy/' to fix."
    BLACK_FAILED=1
}

# Run isort import sorting
echo ""
echo "📚 Running isort import sorting..."
isort --profile black --line-length 100 --check-only --diff cloudy/ || {
    echo "❌ Import sorting issues found. Run 'isort --profile black --line-length 100 cloudy/' to fix."
    ISORT_FAILED=1
}

# Run flake8 linting
echo ""
echo "🐍 Running flake8 linting..."
flake8 --max-line-length=100 --extend-ignore=E203,W503 cloudy/ || {
    echo "❌ Flake8 linting issues found."
    FLAKE8_FAILED=1
}

# Run mypy type checking (optional, may have many issues initially)
echo ""
echo "🔧 Running mypy type checking..."
mypy cloudy/ --ignore-missing-imports --no-strict-optional 2>/dev/null || {
    echo "⚠️  MyPy found type issues (this is expected initially)"
    MYPY_FAILED=1
}

# Summary
echo ""
echo "📊 Linting Summary:"
echo "=================="

if [[ "$BLACK_FAILED" == "1" ]]; then
    echo "❌ Black: FAILED"
else
    echo "✅ Black: PASSED"
fi

if [[ "$ISORT_FAILED" == "1" ]]; then
    echo "❌ isort: FAILED"
else
    echo "✅ isort: PASSED"
fi

if [[ "$FLAKE8_FAILED" == "1" ]]; then
    echo "❌ flake8: FAILED"
else
    echo "✅ flake8: PASSED"
fi

if [[ "$MYPY_FAILED" == "1" ]]; then
    echo "⚠️  mypy: ISSUES (non-blocking)"
else
    echo "✅ mypy: PASSED"
fi

# Exit with error if critical tools failed
if [[ "$BLACK_FAILED" == "1" || "$ISORT_FAILED" == "1" || "$FLAKE8_FAILED" == "1" ]]; then
    echo ""
    echo "❌ Linting failed! Please fix the issues above."
    exit 1
fi

echo ""
echo "✅ All critical linting checks passed!"
echo ""
echo "💡 To auto-fix formatting issues, run:"
echo "   black --line-length 100 cloudy/"
echo "   isort --profile black --line-length 100 cloudy/"