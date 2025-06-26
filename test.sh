#!/usr/bin/env bash
# Python Cloudy Test Script
# 
# This script runs the minimal test suite to ensure core functionality
# doesn't break during development.

set -e  # Exit on any error

echo "🧪 Python Cloudy Test Script"
echo "============================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Run './bootstrap.sh' to set up the environment first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if we're in the right directory (should have fabfile.py)
if [ ! -f "fabfile.py" ]; then
    echo "❌ Error: fabfile.py not found!"
    echo "💡 Make sure you're running this from the python-cloudy project root."
    exit 1
fi

# Run the test suite
echo "🚀 Running test suite..."
echo ""

python tests/test_runner.py

# Get the exit code from the test runner
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests completed successfully!"
else
    echo "❌ Tests failed with exit code: $TEST_EXIT_CODE"
    exit $TEST_EXIT_CODE
fi

echo ""
echo "🎯 Test script completed successfully!"