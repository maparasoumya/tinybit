import redis
from django.conf import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _url_key(code):
    return f"url:{code}"


def _click_key(code):
    return f"clicks:{code}"


def get_cached_url(code):
    return redis_client.get(_url_key(code))


def set_cached_url(code, long_url, ttl=None):
    ttl = ttl or settings.CACHE_TTL_SECONDS
    redis_client.set(_url_key(code), long_url, ex=ttl)


def delete_cached_url(code):
    redis_client.delete(_url_key(code))


def increment_click_counter(code):
    redis_client.incr(_click_key(code))


def pop_pending_clicks(code):
    key = _click_key(code)
    pipe = redis_client.pipeline()
    pipe.get(key)
    pipe.delete(key)
    value, _ = pipe.execute()
    return int(value) if value else 0


def get_pending_clicks(code):
    value = redis_client.get(_click_key(code))
    return int(value) if value else 0


def check_rate_limit(ip):
    key = f"ratelimit:{ip}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 60)

    ttl = redis_client.ttl(key)
    flag = count <= 10

    return flag, ttl