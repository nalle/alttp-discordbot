import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_host = os.environ.get('REDIS_HOST') or "127.0.0.1"
redis_port = os.environ.get('REDIS_PORT') or 6379
redis_password = os.environ.get('REDIS_PASSWORD') or None

if redis_password is not None:
    redis_url = "redis://:{}@{}:{}".format(redis_password, redis_host, redis_port)
else: 
    redis_url = "redis://{}:{}".format(redis_password, redis_host, redis_port)

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
