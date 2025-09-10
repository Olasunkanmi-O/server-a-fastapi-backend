import asyncpg
from app.config import settings

_pool = None

async def init_db_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL, min_size=1, max_size=10)
    return _pool

async def get_pool():
    if _pool is None:
        await init_db_pool()
    return _pool

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None



# import asyncpg
# import logging
# from app.config import settings

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger("db")

# _pool = None

# class LoggingConnection(asyncpg.Connection):
#     async def execute(self, query, *args, **kwargs):
#         logger.debug(f"SQL EXECUTE: {query} | args={args}")
#         return await super().execute(query, *args, **kwargs)

#     async def fetch(self, query, *args, **kwargs):
#         logger.debug(f"SQL FETCH: {query} | args={args}")
#         return await super().fetch(query, *args, **kwargs)

#     async def fetchrow(self, query, *args, **kwargs):
#         logger.debug(f"SQL FETCHROW: {query} | args={args}")
#         return await super().fetchrow(query, *args, **kwargs)

#     async def fetchval(self, query, *args, **kwargs):
#         logger.debug(f"SQL FETCHVAL: {query} | args={args}")
#         return await super().fetchval(query, *args, **kwargs)

# async def init_db_pool():
#     global _pool
#     if _pool is None:
#         _pool = await asyncpg.create_pool(
#             dsn=settings.DATABASE_URL,
#             min_size=1,
#             max_size=10,
#             connection_class=LoggingConnection,  # 👈 use custom connection
#         )
#     return _pool

# async def get_pool():
#     if _pool is None:
#         await init_db_pool()
#     return _pool

# async def close_db_pool():
#     global _pool
#     if _pool:
#         await _pool.close()
#         _pool = None
