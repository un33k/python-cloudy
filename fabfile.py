import logging
from fabric import task
from invoke.collection import Collection
from cloudy.sys import (
    core, docker, etc, python, firewall, memcached, mount, openvpn, ports,
    postfix, python, redis, security, ssh, swap, timezone, user, vim
)
from cloudy.db import psql, pgis, mysql, pgpool, pgbouncer
from cloudy.srv import (
    recipe_cache_redis,
    recipe_generic_server,
    recipe_webserver_django,
    recipe_database_psql_gis,
    recipe_loadbalancer_nginx, 
    recipe_standalone_server, 
    recipe_vpn_server
)
logging.getLogger().setLevel(logging.ERROR)

# Automatically register all tasks in this file
ns = Collection.from_module(__import__(__name__))

ns.add_collection(Collection.from_module(core), name='core')
ns.add_collection(Collection.from_module(docker), name='docker')
ns.add_collection(Collection.from_module(etc), name='etc')
ns.add_collection(Collection.from_module(python), name='python')
ns.add_collection(Collection.from_module(firewall), name='firewall')
ns.add_collection(Collection.from_module(memcached), name='memcached')
ns.add_collection(Collection.from_module(mount), name='mount')
ns.add_collection(Collection.from_module(openvpn), name='openvpn')
ns.add_collection(Collection.from_module(ports), name='ports')
ns.add_collection(Collection.from_module(postfix), name='postfix')
ns.add_collection(Collection.from_module(python), name='python')
ns.add_collection(Collection.from_module(redis), name='redis')
ns.add_collection(Collection.from_module(security), name='security')
ns.add_collection(Collection.from_module(ssh), name='ssh')
ns.add_collection(Collection.from_module(swap), name='swap')
ns.add_collection(Collection.from_module(timezone), name='timezone')
ns.add_collection(Collection.from_module(user), name='user')
ns.add_collection(Collection.from_module(vim), name='vim')
ns.add_collection(Collection.from_module(psql), name='psql')
ns.add_collection(Collection.from_module(pgis), name='pgis')
ns.add_collection(Collection.from_module(mysql), name='mysql')
ns.add_collection(Collection.from_module(pgpool), name='pgpool')
ns.add_collection(Collection.from_module(pgbouncer), name='pgbouncer')


ns.add_collection(Collection.from_module(recipe_cache_redis), name='recipe_cache_redis')
ns.add_collection(Collection.from_module(recipe_generic_server), name='recipe_generic_server')
ns.add_collection(Collection.from_module(recipe_webserver_django), name='recipe_webserver_django')
ns.add_collection(Collection.from_module(recipe_database_psql_gis), name='recipe_database_psql_gis')
ns.add_collection(Collection.from_module(recipe_loadbalancer_nginx), name='recipe_loadbalancer_nginx')
ns.add_collection(Collection.from_module(recipe_standalone_server), name='recipe_standalone_server')
ns.add_collection(Collection.from_module(recipe_vpn_server), name='recipe_vpn_server')

