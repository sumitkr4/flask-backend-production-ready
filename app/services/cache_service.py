class BaseCacheService:
    def get(self, key: str):
        raise NotImplementedError

    def set(self, key: str, value, ttl: int | None = None):
        raise NotImplementedError


class NullCacheService(BaseCacheService):
    # Placeholder implementation so Redis can be added later without changing routes/services.
    def get(self, key: str):
        return None

    def set(self, key: str, value, ttl: int | None = None):
        return True
