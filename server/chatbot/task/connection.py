from os import environ

from saq import Queue

from chatbot.config import REDIS_URL

_queue_url = environ.get("BROKER_URL", REDIS_URL)
queue: Queue = Queue.from_url(_queue_url)
