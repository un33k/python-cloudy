#!/usr/bin/env python
"""
Minimal test suite for Python Cloudy - ensures core functionality doesn't break during development.

This test suite focuses on:
1. Import integrity - all modules can be imported
2. Task discovery - Fabric can find and load all tasks
3. Command structure - hierarchical namespaces work correctly
4. Configuration system - basic config loading works
"""

import sys
import unittest
from unittest.mock import Mock, patch
import importlib


class TestImports(unittest.TestCase):
    """Test that all core modules can be imported without errors."""

    def test_sys_modules_import(self):
        """Test that all sys modules can be imported."""
        sys_modules = [
            'cloudy.sys.core',
            'cloudy.sys.user', 
            'cloudy.sys.ssh',
            'cloudy.sys.firewall',
            'cloudy.sys.python',
            'cloudy.sys.security',
        ]
        
        for module_name in sys_modules:
            with self.subTest(module=module_name):
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")

    def test_db_modules_import(self):
        """Test that all database modules can be imported."""
        db_modules = [
            'cloudy.db.psql',
            'cloudy.db.mysql',
            'cloudy.db.pgbouncer',
            'cloudy.db.pgpool',
            'cloudy.db.pgis',
        ]
        
        for module_name in db_modules:
            with self.subTest(module=module_name):
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")

    def test_web_modules_import(self):
        """Test that all web modules can be imported."""
        web_modules = [
            'cloudy.web.apache',
            'cloudy.web.nginx',
            'cloudy.web.supervisor',
            'cloudy.web.www',
            'cloudy.web.geoip',
        ]
        
        for module_name in web_modules:
            with self.subTest(module=module_name):
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")

    def test_aws_modules_import(self):
        """Test that AWS modules can be imported."""
        try:
            importlib.import_module('cloudy.aws.ec2')
        except ImportError as e:
            self.fail(f"Failed to import cloudy.aws.ec2: {e}")

    def test_recipe_modules_import(self):
        """Test that recipe modules can be imported."""
        recipe_modules = [
            'cloudy.srv.recipe_generic_server',
            'cloudy.srv.recipe_cache_redis',
            'cloudy.srv.recipe_database_psql_gis',
            'cloudy.srv.recipe_webserver_django',
            'cloudy.srv.recipe_loadbalancer_nginx',
            'cloudy.srv.recipe_vpn_server',
            'cloudy.srv.recipe_standalone_server',
        ]
        
        for module_name in recipe_modules:
            with self.subTest(module=module_name):
                try:
                    importlib.import_module(module_name)
                except ImportError as e:
                    self.fail(f"Failed to import {module_name}: {e}")


class TestFabfileStructure(unittest.TestCase):
    """Test that the fabfile.py can be loaded and has the expected structure."""

    def test_fabfile_import(self):
        """Test that fabfile.py can be imported."""
        try:
            import fabfile
            self.assertTrue(hasattr(fabfile, 'ns'))
        except ImportError as e:
            self.fail(f"Failed to import fabfile: {e}")

    def test_command_namespaces_exist(self):
        """Test that expected command namespaces exist."""
        import fabfile
        
        expected_collections = [
            'recipe',
            'sys', 
            'db',
            'web',
            'fw',
            'security',
            'services',
            'storage',
            'aws',
        ]
        
        # Get all collection names from the namespace
        collection_names = []
        for name, item in fabfile.ns.collections.items():
            collection_names.append(name)
        
        for expected in expected_collections:
            with self.subTest(collection=expected):
                self.assertIn(expected, collection_names, 
                            f"Expected collection '{expected}' not found in fabfile")

    def test_recipe_commands_exist(self):
        """Test that recipe commands exist with expected names."""
        import fabfile
        
        recipe_collection = fabfile.ns.collections.get('recipe')
        self.assertIsNotNone(recipe_collection, "Recipe collection not found")
        
        expected_recipes = [
            'gen-install',
            'redis-install', 
            'psql-install',
            'web-install',
            'lb-install',
            'vpn-install',
            'sta-install',
        ]
        
        recipe_tasks = list(recipe_collection.tasks.keys())
        
        for expected in expected_recipes:
            with self.subTest(recipe=expected):
                self.assertIn(expected, recipe_tasks,
                            f"Expected recipe '{expected}' not found")

    def test_db_commands_exist(self):
        """Test that database command structure exists."""
        import fabfile
        
        db_collection = fabfile.ns.collections.get('db')
        self.assertIsNotNone(db_collection, "DB collection not found")
        
        expected_subcollections = ['pg', 'my', 'pgb', 'pgp', 'gis']
        
        for expected in expected_subcollections:
            with self.subTest(subcollection=expected):
                self.assertIn(expected, db_collection.collections,
                            f"Expected DB subcollection '{expected}' not found")


class TestConfigurationSystem(unittest.TestCase):
    """Test that the configuration system works correctly."""

    def test_config_import(self):
        """Test that configuration classes can be imported."""
        try:
            from cloudy.util.conf import CloudyConfig
            self.assertTrue(callable(CloudyConfig))
        except ImportError as e:
            self.fail(f"Failed to import CloudyConfig: {e}")

    @patch('cloudy.util.conf.os.path.exists')
    def test_config_instantiation(self, mock_exists):
        """Test that CloudyConfig can be instantiated."""
        mock_exists.return_value = False  # Mock that config files don't exist
        
        try:
            from cloudy.util.conf import CloudyConfig
            config = CloudyConfig([])  # Empty config list
            self.assertIsNotNone(config)
        except Exception as e:
            self.fail(f"Failed to instantiate CloudyConfig: {e}")


class TestTaskDiscovery(unittest.TestCase):
    """Test that Fabric can discover tasks correctly."""

    def test_fabric_task_discovery(self):
        """Test that Fabric can discover all tasks without errors."""
        import subprocess
        import os
        
        # Change to project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Run fab -l to test task discovery
            result = subprocess.run(
                ['fab', '-l'], 
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check that fab -l completed successfully
            self.assertEqual(result.returncode, 0, 
                           f"fab -l failed with error: {result.stderr}")
            
            # Check that we have a reasonable number of commands
            lines = result.stdout.split('\n')
            # Count lines that contain task names (have two spaces at start for task listing)
            task_lines = [line for line in lines if line.strip() and 
                         (line.startswith('  ') and not line.startswith('   '))]
            
            # We should have at least 50 commands (we know we have ~127)
            self.assertGreater(len(task_lines), 50, 
                             f"Too few commands discovered by Fabric. Found {len(task_lines)} tasks")
            
            # Check for key command patterns
            output = result.stdout
            self.assertIn('recipe.', output, "Recipe commands not found")
            self.assertIn('sys.', output, "System commands not found") 
            self.assertIn('db.', output, "Database commands not found")
            self.assertIn('web.', output, "Web commands not found")
            
        except subprocess.TimeoutExpired:
            self.fail("fab -l command timed out")
        except Exception as e:
            self.fail(f"Error running fab -l: {e}")


def run_minimal_tests():
    """Run the minimal test suite and return results."""
    print("🧪 Running Python Cloudy minimal test suite...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestImports,
        TestFabfileStructure, 
        TestConfigurationSystem,
        TestTaskDiscovery,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All minimal tests passed!")
        print(f"   Ran {result.testsRun} tests successfully")
    else:
        print("❌ Some tests failed!")
        print(f"   Ran {result.testsRun} tests")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_minimal_tests()
    sys.exit(0 if success else 1)