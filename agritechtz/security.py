"""Configure security measures to protect public API against malicious requests"""

from slowapi import Limiter
from slowapi.util import get_remote_address


from agritechtz.cache_config import redis_url


limiter = Limiter(key_func=get_remote_address, storage_uri=redis_url)
"""
Configure rate limiter against DoS attacks
"""
