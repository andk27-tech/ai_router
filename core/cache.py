import hashlib

_cache = {}

def make_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def get_cache(text: str):
    key = make_key(text)
    if key in _cache:
        print("🔥 CACHE HIT")
        return _cache[key]
    print("❄ CACHE MISS")
    return None

def set_cache(text: str, value: str):
    _cache[make_key(text)] = value
