# utils.py
import json
from datetime import date, datetime
from app.database import get_redis

CACHE_EXPIRE_TIME = 60 * 5  # Cache expires after 5 minutes

def serialize_value(value):
    """Recursively convert dates and datetimes to ISO format strings."""
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, (date, datetime)):
        return value.isoformat()  # Convert date / datetime to ISO format string
    return value

async def get_cache(key: str):
    redis = await get_redis()
    cached_data = await redis.get(key)
    if cached_data:
        return json.loads(cached_data)
    return None

async def set_cache(key: str, value):
    redis = await get_redis()
    if value is not None:
        if isinstance(value, list):
            value_to_cache = [serialize_value(item_to_dict(item)) for item in value]
        else:
            value_to_cache = serialize_value(item_to_dict(value))

        await redis.set(key, json.dumps(value_to_cache))
        await redis.expire(key, CACHE_EXPIRE_TIME)
    else:
        await redis.delete(key)

def item_to_dict(item):
    """Convert a Pydantic or SQLAlchemy model to a dictionary."""
    if hasattr(item, 'dict'):
        return item.dict() 
    else:
        item_dict = {col.name: getattr(item, col.name) for col in item.__table__.columns}
        if hasattr(item, 'books'):
            item_dict['books'] = [item_to_dict(book) for book in item.books]
        return item_dict

