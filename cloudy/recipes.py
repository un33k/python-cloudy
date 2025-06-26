"""
Simplified recipe system for Python Cloudy.

This module provides intuitive recipe commands for common server setups.
"""

from fabric import task

from cloudy.srv import (
    recipe_cache_redis,
    recipe_database_psql_gis,
    recipe_generic_server,
    recipe_loadbalancer_nginx,
    recipe_standalone_server,
    recipe_vpn_server,
    recipe_webserver_django,
)
from cloudy.util.context import Context


@task(name="web")
@Context.wrap_context
def web(c: Context, config: str = None, ssl: bool = False, domain: str = None) -> None:
    """Setup a web server with Django.

    Args:
        config: Configuration preset (django, flask, etc.)
        ssl: Enable SSL/HTTPS
        domain: Domain name for the server

    Example:
        fab -H myserver.com recipe.web --config=django --ssl=true --domain=myapp.com
    """
    # Determine config file based on parameters
    cfg_files = []
    if config == "django":
        cfg_files.append("./.cloudy.web.django")
    elif config == "flask":
        cfg_files.append("./.cloudy.web.flask")
    else:
        cfg_files.append("./.cloudy.web")

    if ssl:
        cfg_files.append("./.cloudy.ssl")

    cfg_file = ",".join(cfg_files) if cfg_files else None
    recipe_webserver_django.setup_web(c, cfg_file)


@task(name="database")
@Context.wrap_context
def database(c: Context, type: str = "postgresql", gis: bool = False, config: str = None) -> None:
    """Setup a database server.

    Args:
        type: Database type (postgresql, mysql)
        gis: Enable PostGIS for geographical data
        config: Configuration preset

    Example:
        fab -H myserver.com recipe.database --type=postgresql --gis=true
    """
    cfg_files = []
    if config:
        cfg_files.append(f"./.cloudy.db.{config}")
    elif type == "postgresql":
        if gis:
            cfg_files.append("./.cloudy.db.postgis")
        else:
            cfg_files.append("./.cloudy.db.postgresql")

    cfg_file = ",".join(cfg_files) if cfg_files else None

    if type == "postgresql" and gis:
        recipe_database_psql_gis.setup_db(c, cfg_file)
    else:
        # For now, default to PostGIS setup as that's what we have
        recipe_database_psql_gis.setup_db(c, cfg_file)


@task(name="cache")
@Context.wrap_context
def cache(c: Context, type: str = "redis", config: str = None) -> None:
    """Setup a cache server.

    Args:
        type: Cache type (redis, memcached)
        config: Configuration preset

    Example:
        fab -H myserver.com recipe.cache --type=redis
    """
    cfg_files = []
    if config:
        cfg_files.append(f"./.cloudy.cache.{config}")
    else:
        cfg_files.append(f"./.cloudy.cache.{type}")

    cfg_file = ",".join(cfg_files) if cfg_files else None

    if type == "redis":
        recipe_cache_redis.setup_redis(c, cfg_file)
    else:
        # Default to redis for now
        recipe_cache_redis.setup_redis(c, cfg_file)


@task(name="loadbalancer")
@Context.wrap_context
def loadbalancer(c: Context, type: str = "nginx", ssl: bool = False, config: str = None) -> None:
    """Setup a load balancer.

    Args:
        type: Load balancer type (nginx, apache)
        ssl: Enable SSL termination
        config: Configuration preset

    Example:
        fab -H myserver.com recipe.loadbalancer --type=nginx --ssl=true
    """
    cfg_files = []
    if config:
        cfg_files.append(f"./.cloudy.lb.{config}")
    else:
        cfg_files.append(f"./.cloudy.lb.{type}")

    if ssl:
        cfg_files.append("./.cloudy.ssl")

    cfg_file = ",".join(cfg_files) if cfg_files else None
    recipe_loadbalancer_nginx.setup_lb(c, cfg_file)


@task(name="vpn")
@Context.wrap_context
def vpn(c: Context, type: str = "openvpn", config: str = None) -> None:
    """Setup a VPN server.

    Args:
        type: VPN type (openvpn, wireguard)
        config: Configuration preset

    Example:
        fab -H myserver.com recipe.vpn --type=openvpn
    """
    cfg_files = []
    if config:
        cfg_files.append(f"./.cloudy.vpn.{config}")
    else:
        cfg_files.append(f"./.cloudy.vpn.{type}")

    cfg_file = ",".join(cfg_files) if cfg_files else None
    recipe_vpn_server.setup_openvpn(c, cfg_file)


@task(name="server")
@Context.wrap_context
def server(c: Context, type: str = "generic", config: str = None) -> None:
    """Setup a basic server with common tools.

    Args:
        type: Server type (generic, standalone)
        config: Configuration preset

    Example:
        fab -H myserver.com recipe.server --type=generic
    """
    cfg_files = []
    if config:
        cfg_files.append(f"./.cloudy.server.{config}")
    else:
        cfg_files.append(f"./.cloudy.server.{type}")

    cfg_file = ",".join(cfg_files) if cfg_files else None

    if type == "standalone":
        recipe_standalone_server.setup_standalone(c, cfg_file)
    else:
        recipe_generic_server.setup_server(c, cfg_file)


@task(name="full-stack")
@Context.wrap_context
def full_stack(c: Context, config: str = None) -> None:
    """Setup a complete full-stack server (web + database + cache).

    Args:
        config: Configuration preset

    Example:
        fab -H myserver.com recipe.full-stack --config=django-postgres-redis
    """
    # Setup basic server first
    server(c, "generic", config)

    # Setup database
    database(c, "postgresql", gis=True, config=config)

    # Setup cache
    cache(c, "redis", config=config)

    # Setup web server
    web(c, "django", ssl=True, config=config)


# Aliases for backward compatibility and convenience
@task(name="django")
@Context.wrap_context
def django(c: Context, ssl: bool = True, domain: str = None) -> None:
    """Quick setup for Django web server.

    Example:
        fab -H myserver.com recipe.django --domain=myapp.com
    """
    web(c, "django", ssl, domain)


@task(name="postgres")
@Context.wrap_context
def postgres(c: Context, gis: bool = True) -> None:
    """Quick setup for PostgreSQL database.

    Example:
        fab -H myserver.com recipe.postgres --gis=true
    """
    database(c, "postgresql", gis)


@task(name="nginx-lb")
@Context.wrap_context
def nginx_lb(c: Context, ssl: bool = True) -> None:
    """Quick setup for Nginx load balancer.

    Example:
        fab -H myserver.com recipe.nginx-lb --ssl=true
    """
    loadbalancer(c, "nginx", ssl)
