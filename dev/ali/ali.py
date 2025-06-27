#!/usr/bin/env python3
"""
Ali (Ansible Line Interpreter) - Simplified Ansible CLI for Cloudy

Makes Ansible commands shorter and more intuitive:
  ali security       → ansible-playbook -i cloudy/inventory/test.yml cloudy/playbooks/recipes/core/security.yml
  ali django --prod  → ansible-playbook -i cloudy/inventory/production.yml cloudy/playbooks/recipes/www/django.yml
"""

import os
import sys
import glob
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log(message: str, color: str = Colors.GREEN) -> None:
    """Print colored log message"""
    print(f"{color}✓{Colors.NC} {message}")

def warn(message: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")

def error(message: str) -> None:
    """Print error message and exit"""
    print(f"{Colors.RED}✗{Colors.NC} {message}")
    sys.exit(1)

def info(message: str) -> None:
    """Print info message"""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")

class AliConfig:
    """Configuration and paths for Ali CLI"""
    
    def __init__(self):
        # Find project root (directory containing cloudy/)
        self.project_root = self._find_project_root()
        self.cloudy_dir = self.project_root / "cloudy"
        self.recipes_dir = self.cloudy_dir / "playbooks" / "recipes"
        self.inventory_dir = self.cloudy_dir / "inventory"
        self.dev_dir = self.project_root / "dev"
        
        # Validate project structure
        self._validate_structure()
        
        # Check virtual environment
        self._check_virtual_environment()
    
    def _find_project_root(self) -> Path:
        """Find the project root directory by looking for cloudy/ folder"""
        current = Path.cwd()
        
        # Check current directory and parents
        for path in [current] + list(current.parents):
            if (path / "cloudy" / "ansible.cfg").exists():
                return path
        
        error("Could not find project root. Run ali from the ansible-cloudy project directory.")
    
    def _validate_structure(self) -> None:
        """Validate that required directories exist"""
        required_paths = [
            self.cloudy_dir,
            self.recipes_dir,
            self.inventory_dir,
        ]
        
        for path in required_paths:
            if not path.exists():
                error(f"Required directory not found: {path}")
    
    def _check_virtual_environment(self) -> None:
        """Check if virtual environment is properly activated"""
        venv_path = self.project_root / ".venv"
        
        # Check if .venv exists
        if not venv_path.exists():
            error("Virtual environment not found!\n"
                  f"{Colors.YELLOW}Run bootstrap to create it:{Colors.NC}\n"
                  "  ./bootstrap.sh\n"
                  f"{Colors.YELLOW}Then activate and try again:{Colors.NC}\n"
                  "  source .venv/bin/activate")
        
        # Check if we're in a virtual environment
        if not os.environ.get('VIRTUAL_ENV'):
            error("Virtual environment not activated!\n"
                  f"{Colors.YELLOW}Activate the environment first:{Colors.NC}\n"
                  "  source .venv/bin/activate\n"
                  f"{Colors.YELLOW}Then run ali commands:{Colors.NC}\n"
                  "  ./ali dev syntax")
        
        # Check if ansible is available in the venv
        try:
            import importlib.util
            ansible_spec = importlib.util.find_spec("ansible")
            if ansible_spec is None:
                error("Ansible not found in virtual environment!\n"
                      f"{Colors.YELLOW}Run bootstrap to install dependencies:{Colors.NC}\n"
                      "  ./bootstrap.sh")
        except ImportError:
            error("Python import system error - virtual environment may be corrupted")

class RecipeFinder:
    """Find and manage recipe files"""
    
    def __init__(self, config: AliConfig):
        self.config = config
        self._recipe_cache = None
    
    def get_all_recipes(self) -> dict:
        """Get all available recipes organized by category"""
        if self._recipe_cache is None:
            self._recipe_cache = self._scan_recipes()
        return self._recipe_cache
    
    def _scan_recipes(self) -> dict:
        """Scan recipes directory and organize by category"""
        recipes = {}
        
        # Scan all yml files in recipes directory
        pattern = str(self.config.recipes_dir / "**" / "*.yml")
        for recipe_path in glob.glob(pattern, recursive=True):
            rel_path = Path(recipe_path).relative_to(self.config.recipes_dir)
            
            # Extract category and name
            if len(rel_path.parts) == 2:  # category/name.yml
                category, filename = rel_path.parts
                name = filename[:-4]  # Remove .yml extension
                
                if category not in recipes:
                    recipes[category] = {}
                recipes[category][name] = str(rel_path)
        
        return recipes
    
    def find_recipe(self, name: str) -> Optional[str]:
        """Find a recipe by name, searching all categories"""
        recipes = self.get_all_recipes()
        
        # First try exact match in any category
        for category, category_recipes in recipes.items():
            if name in category_recipes:
                return category_recipes[name]
        
        # Try partial matches
        matches = []
        for category, category_recipes in recipes.items():
            for recipe_name, recipe_path in category_recipes.items():
                if name in recipe_name:
                    matches.append((recipe_name, recipe_path))
        
        if len(matches) == 1:
            return matches[0][1]
        elif len(matches) > 1:
            error(f"Ambiguous recipe name '{name}'. Found multiple matches: {[m[0] for m in matches]}")
        
        return None

class InventoryManager:
    """Manage inventory files"""
    
    def __init__(self, config: AliConfig):
        self.config = config
    
    def get_inventory_path(self, production: bool = False) -> str:
        """Get the appropriate inventory file path"""
        if production:
            inventory_file = self.config.inventory_dir / "production.yml"
        else:
            inventory_file = self.config.inventory_dir / "test.yml"
        
        if not inventory_file.exists():
            error(f"Inventory file not found: {inventory_file}")
        
        return str(inventory_file)

class AnsibleRunner:
    """Execute ansible-playbook commands"""
    
    def __init__(self, config: AliConfig):
        self.config = config
    
    def run_recipe(self, recipe_path: str, inventory_path: str, 
                   extra_args: List[str], dry_run: bool = False) -> int:
        """Run ansible-playbook with the specified recipe"""
        
        # Build the command
        cmd = [
            "ansible-playbook",
            "-i", inventory_path,
            str(self.config.recipes_dir / recipe_path)
        ]
        
        # Add dry run flag if requested
        if dry_run:
            cmd.append("--check")
        
        # Add any extra arguments
        cmd.extend(extra_args)
        
        # Show what we're running
        info(f"Running: {' '.join(cmd)}")
        
        # Change to cloudy directory for execution
        os.chdir(self.config.cloudy_dir)
        
        # Execute the command
        try:
            return subprocess.run(cmd).returncode
        except KeyboardInterrupt:
            warn("Interrupted by user")
            return 130
        except FileNotFoundError:
            error("ansible-playbook not found. Please install Ansible or activate your virtual environment.")

class DevTools:
    """Development tools and commands"""
    
    def __init__(self, config: AliConfig):
        self.config = config
    
    def validate(self) -> int:
        """Run comprehensive validation"""
        validate_script = self.config.dev_dir / "validate.py"
        if not validate_script.exists():
            error(f"Validation script not found: {validate_script}")
        
        info(f"Running comprehensive validation...")
        os.chdir(self.config.project_root)
        
        result = subprocess.run([str(validate_script)], capture_output=True, text=True)
        
        if result.returncode != 0:
            # Check if it's a missing dependency issue
            if "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr:
                warn("Validation script requires additional Python packages")
                warn("Install with: pip install pyyaml")
                warn("Falling back to syntax check only...")
                return self.syntax()
            else:
                # Print the actual error output
                if result.stderr:
                    print(result.stderr)
                if result.stdout:
                    print(result.stdout)
        else:
            # Print successful output
            if result.stdout:
                print(result.stdout)
        
        return result.returncode
    
    def syntax(self) -> int:
        """Run syntax checking"""
        syntax_script = self.config.dev_dir / "syntax-check.sh"
        if not syntax_script.exists():
            error(f"Syntax check script not found: {syntax_script}")
        
        info(f"Running syntax checks...")
        os.chdir(self.config.project_root)
        return subprocess.run([str(syntax_script)]).returncode
    
    def lint(self) -> int:
        """Run ansible-lint"""
        lint_config = self.config.dev_dir / ".ansible-lint.yml"
        if not lint_config.exists():
            warn("Ansible-lint config not found, using defaults")
            config_args = []
        else:
            config_args = ["-c", str(lint_config)]
        
        info(f"Running ansible-lint...")
        os.chdir(self.config.project_root)
        
        try:
            cmd = ["ansible-lint"] + config_args + [str(self.config.recipes_dir)]
            return subprocess.run(cmd).returncode
        except FileNotFoundError:
            error("ansible-lint not found. Install with: pip install ansible-lint")
    
    def test(self) -> int:
        """Run authentication tests"""
        test_playbook = self.config.dev_dir / "test-auth.yml"
        if not test_playbook.exists():
            error(f"Test playbook not found: {test_playbook}")
        
        inventory_path = self.config.inventory_dir / "test.yml"
        if not inventory_path.exists():
            error(f"Test inventory not found: {inventory_path}")
        
        info(f"Running authentication tests...")
        os.chdir(self.config.cloudy_dir)
        
        cmd = [
            "ansible-playbook",
            "-i", str(inventory_path),
            str(test_playbook),
            "--check"
        ]
        
        return subprocess.run(cmd).returncode
    
    def spell(self) -> int:
        """Run spell checking"""
        spell_config = self.config.dev_dir / ".cspell.json"
        if not spell_config.exists():
            error(f"Spell check config not found: {spell_config}")
        
        info(f"Running spell check...")
        os.chdir(self.config.project_root)
        
        try:
            cmd = ["npx", "cspell", "**/*.md", "**/*.yml", "--config", str(spell_config)]
            return subprocess.run(cmd).returncode
        except FileNotFoundError:
            error("cspell not found. Install with: npm install -g cspell")

def list_dev_commands() -> None:
    """List available development commands"""
    print(f"\n{Colors.CYAN}🛠️  Development Commands:{Colors.NC}")
    print("=" * 50)
    
    commands = [
        ("validate", "Comprehensive validation of all components"),
        ("syntax", "Quick syntax checking for all recipes"),
        ("lint", "Ansible-lint validation"),
        ("test", "Authentication flow testing"),
        ("spell", "Spell check all documentation and configs"),
    ]
    
    for cmd, desc in commands:
        print(f"  • {Colors.GREEN}ali dev {cmd:<8}{Colors.NC} - {desc}")
    
    print(f"\n{Colors.YELLOW}Usage examples:{Colors.NC}")
    print("  ali dev validate       # Full validation suite")
    print("  ali dev syntax         # Quick syntax check")
    print("  ali dev lint           # Ansible linting")
    print("  ali dev test           # Test authentication")

def list_recipes(config: AliConfig) -> None:
    """List all available recipes"""
    finder = RecipeFinder(config)
    recipes = finder.get_all_recipes()
    
    if not recipes:
        warn("No recipes found")
        return
    
    print(f"\n{Colors.CYAN}📋 Available Recipes:{Colors.NC}")
    print("=" * 50)
    
    for category in sorted(recipes.keys()):
        print(f"\n{Colors.BLUE}{category.upper()}:{Colors.NC}")
        for recipe_name in sorted(recipes[category].keys()):
            print(f"  • {recipe_name}")
    
    print(f"\n{Colors.YELLOW}Usage examples:{Colors.NC}")
    print("  ali security           # Run core/security.yml on test")
    print("  ali django --prod      # Run www/django.yml on production")
    print("  ali redis --check      # Dry run cache/redis.yml")
    print("  ali nginx -- --tags ssl # Pass --tags ssl to ansible-playbook")

def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Ali (Ansible Line Interpreter) - Simplified Ansible CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ali security                    Run security recipe on test environment
  ali django --prod              Run django recipe on production
  ali redis --check              Dry run redis recipe
  ali nginx -- --tags ssl        Pass --tags ssl to ansible-playbook
  ali --list                      Show all available recipes
  
  ali dev validate                Run comprehensive validation
  ali dev syntax                 Quick syntax checking
  ali dev lint                   Ansible linting
  ali dev test                   Authentication testing
        """
    )
    
    parser.add_argument("command", nargs="?", help="Recipe name or 'dev' for development commands")
    parser.add_argument("subcommand", nargs="?", help="Development subcommand (when using 'dev')")
    parser.add_argument("--prod", "--production", action="store_true",
                       help="Use production inventory instead of test")
    parser.add_argument("--check", "--dry-run", action="store_true",
                       help="Run in dry-run mode (--check)")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List all available recipes or dev commands")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    return parser

def main() -> None:
    """Main entry point for Ali CLI"""
    
    # Parse arguments, splitting on -- for ansible args
    if "--" in sys.argv:
        split_idx = sys.argv.index("--")
        ali_args = sys.argv[1:split_idx]
        ansible_args = sys.argv[split_idx + 1:]
    else:
        ali_args = sys.argv[1:]
        ansible_args = []
    
    # Parse ali arguments
    parser = create_parser()
    args = parser.parse_args(ali_args)
    
    # Initialize configuration
    try:
        config = AliConfig()
    except Exception as e:
        error(f"Configuration error: {e}")
    
    # Handle list command
    if args.list:
        if args.command == "dev":
            list_dev_commands()
        else:
            list_recipes(config)
        return
    
    # Handle dev commands
    if args.command == "dev":
        if not args.subcommand:
            list_dev_commands()
            return
        
        dev_tools = DevTools(config)
        
        # Route to appropriate dev command
        if args.subcommand == "validate":
            exit_code = dev_tools.validate()
        elif args.subcommand == "syntax":
            exit_code = dev_tools.syntax()
        elif args.subcommand == "lint":
            exit_code = dev_tools.lint()
        elif args.subcommand == "test":
            exit_code = dev_tools.test()
        elif args.subcommand == "spell":
            exit_code = dev_tools.spell()
        else:
            error(f"Unknown dev command '{args.subcommand}'. Use 'ali dev --list' to see available commands.")
        
        sys.exit(exit_code)
    
    # Require recipe name if not listing or dev command
    if not args.command:
        parser.print_help()
        return
    
    # Find the recipe
    finder = RecipeFinder(config)
    recipe_path = finder.find_recipe(args.command)
    
    if not recipe_path:
        error(f"Recipe '{args.command}' not found. Use 'ali --list' to see available recipes.")
    
    # Get inventory
    inventory_manager = InventoryManager(config)
    inventory_path = inventory_manager.get_inventory_path(args.prod)
    
    # Add verbose flag if requested
    if args.verbose:
        ansible_args.insert(0, "-v")
    
    # Run the recipe
    runner = AnsibleRunner(config)
    exit_code = runner.run_recipe(
        recipe_path=recipe_path,
        inventory_path=inventory_path,
        extra_args=ansible_args,
        dry_run=args.check
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()