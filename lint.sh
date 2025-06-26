#!/usr/bin/env bash

# Modern Python linting script for Python Cloudy
# Uses flake8, black, and mypy for comprehensive code quality checking

set -e

echo "🔍 Python Cloudy Code Quality Check"
echo "=================================="
echo

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Activating .venv..."
    if [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
        echo "✅ Activated virtual environment"
    else
        echo "❌ No .venv found. Please run bootstrap.sh first."
        exit 1
    fi
fi

echo

# Install linting tools if not present
echo "📦 Checking linting tools..."
pip install -q flake8 black isort mypy 2>/dev/null || echo "Linting tools already installed"

echo

# 1. Black - Code formatting check
echo "🎨 Checking code formatting with Black..."
if black --check --diff cloudy/ 2>/dev/null; then
    echo "✅ Code formatting is good"
else
    echo "❌ Code formatting issues found. Run 'black cloudy/' to fix."
    BLACK_FAILED=1
fi

echo

# 2. isort - Import sorting check  
echo "📚 Checking import sorting with isort..."
if isort --check-only --diff cloudy/ 2>/dev/null; then
    echo "✅ Import sorting is good"
else
    echo "❌ Import sorting issues found. Run 'isort cloudy/' to fix."
    ISORT_FAILED=1
fi

echo

# 3. Flake8 - Style and error checking
echo "🔍 Checking code style with Flake8..."
if flake8 cloudy/; then
    echo "✅ No style issues found"
else
    echo "❌ Style issues found (see above)"
    FLAKE8_FAILED=1
fi

echo

# 4. Basic type checking with mypy (optional - may have issues with Fabric)
echo "🔬 Running basic type checking with mypy..."
if mypy cloudy/ 2>/dev/null; then
    echo "✅ No major type issues found"
else
    echo "⚠️  Type checking completed with warnings (this is normal for Fabric code)"
fi

echo
echo "📋 Summary"
echo "=========="

if [[ -z "$BLACK_FAILED" && -z "$ISORT_FAILED" && -z "$FLAKE8_FAILED" ]]; then
    echo "✅ All checks passed! Code quality is excellent."
    exit 0
else
    echo "❌ Some checks failed:"
    [[ -n "$BLACK_FAILED" ]] && echo "  - Code formatting (run: black cloudy/)"
    [[ -n "$ISORT_FAILED" ]] && echo "  - Import sorting (run: isort cloudy/)"
    [[ -n "$FLAKE8_FAILED" ]] && echo "  - Style issues (see flake8 output above)"
    echo
    echo "💡 To auto-fix formatting issues:"
    echo "   black cloudy/ && isort cloudy/"
    exit 1
fi