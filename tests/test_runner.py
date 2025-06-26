#!/usr/bin/env python
"""
Python Cloudy Test Runner

This runs the minimal test suite to ensure core functionality works during development.
"""

import sys
import os

# Add parent directory to path so we can import cloudy modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    from test_minimal import run_minimal_tests

    print("🚀 Python Cloudy Development Test Suite")
    print("=" * 50)

    success = run_minimal_tests()

    if success:
        print("\n🎉 All tests passed! The core functionality is working correctly.")
    else:
        print("\n💥 Some tests failed! Please check the output above.")

    sys.exit(0 if success else 1)
