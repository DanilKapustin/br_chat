from redis.asyncio.client import Redis, PubSub

from chatbot.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

_connection: Redis = Redis(
    host=REDIS_HOST,
    port=int(REDIS_PORT),
    decode_responses=True,
    password=REDIS_PASSWORD,
)


async def subscribe(channel_name: str) -> PubSub:
    """Subscribe redis channel"""
    global _connection
    channel: PubSub = _connection.pubsub()

    await channel.subscribe(channel_name)

    return channel


async def publish(channel_name: str, message: str):
    """Publish message to redis channel"""
    global _connection
    await _connection.publish(channel_name, message)
