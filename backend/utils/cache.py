import config
import redis
from config import logger

RE = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    password=config.REDIS_PASSWORD,
    charset="utf-8",
    decode_responses=True,
)


def get_cache(attr: str):
    """Retrieve attribute from redis cache.

    Args:
        attr (str): Cache attribute key to retrieve
    """
    try:
        value = RE.get(attr)
        logger.debug(f"Retrieve cache {attr}: {value}")
    except Exception as e:
        value = None
        logger.error(f"Error retrieve cache {attr}. {e}")

    return value


def set_cache(attr: str, value: str):
    """Set the attribute & value to redis cache.

    Args:
        attr (str): Attribute to set in cache
        value (str): Value to set in cache
    """
    try:
        RE.set(attr, value)
        logger.debug(f"Set cache {attr}: {value}")
    except Exception as e:
        logger.error(f"Error setting cache {attr}: {value}. {e}")


def del_cache(attr: str):
    """Delete attribute from redis cache.

    Args:
        attr (str): Attribute to delete in cache
    """
    try:
        RE.delete(attr)
        logger.debug(f"Delete cache {attr}")
    except Exception as e:
        logger.error(f"Error deleting cache {attr}. {e}")
