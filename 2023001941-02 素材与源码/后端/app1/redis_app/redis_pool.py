import redis

# Redis 连接池配置信息
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_POOL_SIZE = 10

# 建立 Redis 连接池
redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    max_connections=REDIS_POOL_SIZE
)
