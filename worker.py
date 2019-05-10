import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

conn = redis.Redis(host=os.getenv('REDIS_SERVER'), port=6379, password=os.environ.get('REDIS_PASSWORD'))

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
