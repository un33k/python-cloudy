"""Enhanced Fabric Context with smart output control and SSH reconnection."""

import logging
import os
import re
import sys
from functools import wraps
from typing import Callable, List

from colorama import Fore, Style
from fabric import Connection

logger = logging.getLogger("fab-commands")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
logger.propagate = False

# Commands that should ALWAYS show output (informational/status commands)
ALWAYS_SHOW_OUTPUT: List[str] = [
    "ufw status",
    "systemctl status",
    "service status",
    "df",
    "free",
    "ps",
    "netstat",
    "iptables -L",
    "lsblk",
    "mount",
    "who",
    "w",
    "uptime",
    "date",
    "psql --version",
    "pg_lsclusters",
    "apache2ctl status",
    "nginx -t",
    "docker ps",
    "docker images",
    "git status",
    "git log",
    "git diff",
    "tail",
    "head",
    "cat",
    "less",
    "more",
    "ls -la",
    "find",
    "grep",
    "awk",
    "sed -n",  # when used for display
    "echo",
    "printf",
    "hostname",
    "uname",
    "id",
    "whoami",
    "pwd",
    "which",
    "whereis",
]

# Commands that are typically "noisy" and should be hidden by default (regex patterns)
HIDE_BY_DEFAULT_PATTERNS: List[str] = [
    # Package management
    r"apt.*update",
    r"apt.*install",
    r"apt.*upgrade",
    r"apt.*remove",
    r"apt.*autoremove",
    r"apt.*list\s+--upgradable",
    r"apt-get.*update",
    r"apt-get.*install",
    r"apt-get.*upgrade",
    r"yum.*install",
    r"yum.*update",
    r"dnf.*install",
    r"dpkg\s+-i",
    r"dpkg-reconfigure",
    r"rpm\s+-i",
    # Downloads and archives
    r"wget\s+",
    r"curl\s+-.*",  # downloading
    r"unzip\s+",
    r"tar\s+-[xz]",
    r"g?zip\s+",
    r"bunzip2?\s+",
    # Build tools
    r"make\s+",
    r"cmake\s+",
    r"pip.*install",
    r"npm.*install",
    r"yarn.*install",
    r"composer.*install",
    r"bundle.*install",
    r"mvn.*install",
    r"gradle.*build",
    r"go.*build",
    r"cargo.*build",
    # System configuration and services
    r"systemctl\s+(start|stop|reload|restart)",
    r"service\s+.*\s+(start|stop|reload|restart)",
    r"update-alternatives",
    r"debconf-set-selections",
    r"passwd\s+",
    r"chpasswd",
    # File operations
    r"chmod\s+",
    r"chown\s+",
    r"mkdir\s+-p",
    r"ln\s+-sf",
    r"mv\s+",
    r"cp\s+",
    r"rm\s+",
    r"sed\s+-i",
    r"sh\s+-c.*>",  # shell redirects
    r"echo.*>",  # redirect operations
    r"cat.*>>",  # append operations
    # SSH and network
    r"ssh-keygen",
    r"scp\s+",
]


class Context(Connection):
    """
    Enhanced Fabric Connection with smart output control and SSH reconnection.

    Provides intelligent command output filtering, automatic password handling,
    and robust SSH port reconnection for server automation tasks.
    """

    @property
    def verbose(self) -> bool:
        """Check if verbose output is enabled via environment variable or config."""
        # Check environment variable for verbose mode
        if os.environ.get("CLOUDY_VERBOSE", "").lower() in ("1", "true", "yes"):
            return True

        # Check Fabric's built-in debug flag (--debug enables verbose too)
        if hasattr(self.config, "run") and getattr(self.config.run, "echo", False):
            return True

        return getattr(self.config, "cloudy_verbose", False) or getattr(
            self.config, "cloudy_debug", False
        )

    @property
    def debug(self) -> bool:
        """Check if debug output is enabled via Fabric's built-in debug flag."""
        # Check Fabric's built-in debug config
        if hasattr(self.config, "run") and getattr(self.config.run, "echo", False):
            return True

        return getattr(self.config, "cloudy_debug", False)

    def _should_show_output(self, command: str) -> bool:
        """Determine if command output should be shown based on command type."""
        # Debug mode: show everything
        if self.debug:
            return True

        # Verbose mode: show everything
        if self.verbose:
            return True

        cmd_lower = command.lower().strip()

        # Hide noisy commands by default FIRST (regex matching)
        for pattern in HIDE_BY_DEFAULT_PATTERNS:
            if re.search(pattern, cmd_lower):
                return False

        # Always show output for informational commands (substring matching)
        for pattern in ALWAYS_SHOW_OUTPUT:
            if pattern in cmd_lower:
                return True

        # For other commands, show output (conservative approach)
        return True

    def run(self, command, *args, **kwargs):
        print(f"\n{Fore.CYAN}### {command}\n-----------{Style.RESET_ALL}", flush=True)

        show_output = self._should_show_output(command)
        kwargs.setdefault("hide", not show_output)
        kwargs.setdefault("pty", True)

        result = super().run(command, *args, **kwargs)

        # Only show success/failure indicators for commands where we hid the output
        if not show_output:
            if result.failed:
                print(f"{Fore.RED}❌ FAILED{Style.RESET_ALL}")
                if result.stderr:
                    print(f"Error: {result.stderr.strip()}")
                elif result.stdout:
                    print(f"Output: {result.stdout.strip()}")
            else:
                print(f"{Fore.GREEN}✅ SUCCESS{Style.RESET_ALL}")

        return result

    def sudo(self, command, *args, **kwargs):
        print(f"\n{Fore.YELLOW}### {command}\n-----------{Style.RESET_ALL}", flush=True)

        # Check for environment variable and set it if config is None
        env_password = os.environ.get("INVOKE_SUDO_PASSWORD")
        if hasattr(self.config, "sudo") and not self.config.sudo.password and env_password:
            self.config.sudo.password = env_password

        show_output = self._should_show_output(command)
        kwargs.setdefault("hide", not show_output)
        kwargs.setdefault("pty", True)

        result = super().sudo(command, *args, **kwargs)

        # Only show success/failure indicators for commands where we hid the output
        if not show_output:
            if result.failed:
                print(f"{Fore.RED}❌ FAILED{Style.RESET_ALL}")
                if result.stderr:
                    print(f"Error: {result.stderr.strip()}")
                elif result.stdout:
                    print(f"Output: {result.stdout.strip()}")
            else:
                print(f"{Fore.GREEN}✅ SUCCESS{Style.RESET_ALL}")

        return result

    def reconnect(self, new_port: str = "", new_user: str = "") -> "Context":
        """
        Creates and returns a new Context (Connection) object to the same host
        and user, but on a different port, preserving other connection details.

        Args:
            new_port: The new port number to connect to.
            new_user: The new user to connect as.

        Returns:
            A new Context instance connected to the new port, or None if
            reconnection fails.
        """
        # Extract all relevant connection parameters from the current Context instance
        port_to_use = new_port or self.port
        user_to_use = new_user or self.user
        host_to_use = self.host

        print(
            f"\nAttempting to reconnect to {self.host} as user {user_to_use} "
            f"on new port {port_to_use}..."
        )

        connect_kwargs_to_use = {}
        if isinstance(self.connect_kwargs, dict):
            connect_kwargs_to_use = self.connect_kwargs.copy()

        gateway_to_use = self.gateway

        # --- CRITICAL FIX FOR AmbiguousMergeError ---
        # inline_ssh_env should be a Boolean, not a dictionary
        inline_ssh_env_to_use = getattr(self, "inline_ssh_env", False)
        if not isinstance(inline_ssh_env_to_use, bool):
            inline_ssh_env_to_use = False
        # --- END CRITICAL FIX ---

        connect_kwargs_to_use.pop("port", None)
        connect_kwargs_to_use.pop("connect_timeout", None)
        connect_kwargs_to_use.pop("forward_agent", None)

        if self.is_connected:
            self.close()

        # Create a new Context instance with the updated port,
        # while passing all other parameters from the original context.
        new_ctx = Context(
            host=host_to_use,
            user=user_to_use,
            port=port_to_use,
            gateway=gateway_to_use,
            connect_kwargs=connect_kwargs_to_use,
            inline_ssh_env=inline_ssh_env_to_use,  # Use the Boolean value
        )

        try:

            new_ctx.open()  # Explicitly open to test the connection
            new_ctx.run("echo 'Successfully reconnected on new port.'", hide=True)
            print(f"Successfully re-established connection on {new_ctx.host}:{new_ctx.port}")
        except Exception as e:
            print(
                f"CRITICAL ERROR: Failed to reconnect to {self.host} as user {user_to_use} "
                f"on new port {port_to_use}."
            )
            print("Manual intervention may be required!")
            print(f"Error details: {e}")
            if new_ctx and new_ctx.is_connected:
                new_ctx.close()

        return new_ctx

    @staticmethod
    def wrap_context(func: Callable):
        """Decorator to wrap Fabric tasks with enhanced Context functionality."""

        @wraps(func)
        def wrapper(c: Context, *args, **kwargs):
            # Also apply the same robustness for inline_ssh_env and connect_kwargs
            # when the initial Context is created by wrap_context.
            wrapper_connect_kwargs = {}
            if isinstance(c.connect_kwargs, dict):
                wrapper_connect_kwargs = c.connect_kwargs.copy()

            # inline_ssh_env should be a Boolean, not a dictionary
            wrapper_inline_ssh_env = getattr(c, "inline_ssh_env", False)
            if not isinstance(wrapper_inline_ssh_env, bool):
                wrapper_inline_ssh_env = False

            # Fixed: Remove c.config and use getattr to safely access gateway
            ctx = Context(
                host=c.host,
                user=c.user,
                port=c.port,
                gateway=getattr(c, "gateway", None),  # Safely get gateway attribute
                connect_kwargs=wrapper_connect_kwargs,
                inline_ssh_env=wrapper_inline_ssh_env,  # Boolean value
            )
            return func(ctx, *args, **kwargs)

        return wrapper
