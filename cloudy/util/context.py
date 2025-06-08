import logging
import sys
from colorama import Fore, Style
from functools import wraps
from fabric import Connection
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger("fab-commands")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
logger.propagate = False

class Context(Connection):
    def run(self, command, *args, **kwargs):
        print(f"\n{Fore.CYAN}### {command}\n-----------{Style.RESET_ALL}", flush=True)
        kwargs.setdefault("hide", False)
        kwargs.setdefault("pty", True)
        return super().run(command, *args, **kwargs)

    def sudo(self, command, *args, **kwargs):
        print(f"\n{Fore.YELLOW}### {command}\n-----------{Style.RESET_ALL}", flush=True)
        kwargs.setdefault("hide", False)
        kwargs.setdefault("pty", True)
        return super().sudo(command, *args, **kwargs)

    def reconnect(self, new_port: str = '', new_user: str = '') -> 'Context':
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
        
        print(f"\nAttempting to reconnect to {self.host} as user {user_to_use} on new port {port_to_use}...")

        connect_kwargs_to_use = {}
        if isinstance(self.connect_kwargs, dict):
            connect_kwargs_to_use = self.connect_kwargs.copy()

        gateway_to_use = self.gateway

        # --- CRITICAL FIX FOR AmbiguousMergeError ---
        # inline_ssh_env should be a Boolean, not a dictionary
        inline_ssh_env_to_use = getattr(self, 'inline_ssh_env', False)
        if not isinstance(inline_ssh_env_to_use, bool):
            inline_ssh_env_to_use = False
        # --- END CRITICAL FIX ---

        connect_kwargs_to_use.pop('port', None)
        connect_kwargs_to_use.pop('connect_timeout', None)
        connect_kwargs_to_use.pop('forward_agent', None)

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
            inline_ssh_env=inline_ssh_env_to_use, # Use the Boolean value
        )

        try:

            new_ctx.open() # Explicitly open to test the connection
            new_ctx.run("echo 'Successfully reconnected on new port.'", hide=True)
            print(f"Successfully re-established connection on {new_ctx.host}:{new_ctx.port}")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to reconnect to {self.host} as user {user_to_use} on new port {port_to_use}.")
            print(f"Manual intervention may be required!")
            print(f"Error details: {e}")
            if new_ctx and new_ctx.is_connected:
                new_ctx.close()

        return new_ctx

    @staticmethod
    def wrap_context(func: Callable):
        @wraps(func)
        def wrapper(c: Context, *args, **kwargs):
            # Also apply the same robustness for inline_ssh_env and connect_kwargs
            # when the initial Context is created by wrap_context.
            wrapper_connect_kwargs = {}
            if isinstance(c.connect_kwargs, dict):
                wrapper_connect_kwargs = c.connect_kwargs.copy()

            # inline_ssh_env should be a Boolean, not a dictionary
            wrapper_inline_ssh_env = getattr(c, 'inline_ssh_env', False)
            if not isinstance(wrapper_inline_ssh_env, bool):
                wrapper_inline_ssh_env = False

            # Fixed: Remove c.config and use getattr to safely access gateway
            ctx = Context(
                host=c.host,
                user=c.user,
                port=c.port,
                gateway=getattr(c, 'gateway', None),  # Safely get gateway attribute
                connect_kwargs=wrapper_connect_kwargs,
                inline_ssh_env=wrapper_inline_ssh_env, # Boolean value
            )
            return func(ctx, *args, **kwargs)
        return wrapper