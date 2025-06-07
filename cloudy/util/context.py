import logging
import sys
from functools import wraps
from fabric import Connection
from typing import Callable

logger = logging.getLogger("fab-commands")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers = [handler]
logger.propagate = False

class Context(Connection):
    def run(self, command, *args, **kwargs):
        print(f"\n### {command}\n-----------", flush=True)  # replaces logger to ensure immediate output
        kwargs.setdefault("hide", False)
        kwargs.setdefault("pty", True)
        return super().run(command, *args, **kwargs)

    def sudo(self, command, *args, **kwargs):
        print(f"\n### {command}\n-----------", flush=True)
        kwargs.setdefault("hide", False)
        kwargs.setdefault("pty", True)
        return super().sudo(command, *args, **kwargs)

    @staticmethod
    def wrap_context(func: Callable):
        @wraps(func)
        def wrapper(c: Context, *args, **kwargs):
            ctx = Context(
                host=c.host,
                user=c.user,
                port=c.port,
                config=c.config,
                connect_kwargs=c.connect_kwargs,
            )
            return func(ctx, *args, **kwargs)
        return wrapper
