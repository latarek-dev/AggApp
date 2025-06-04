from config import get_redis
from typing import Optional
from decimal import Decimal
from interfaces import ICacheService

class RedisCacheService(ICacheService):
    """Serwis obsługujący cache w Redis."""

    async def get_cached_price(self, key: str) -> Optional[float]:
        """Pobiera wartość z Redis."""
        redis = await get_redis()
        print(f"Połączenie z Redis: {redis}")  # Debugowanie
        price = await redis.get(key)
        if price:
            print(f"Znaleziono cenę w Redis: {price}")
        else:
            print(f"Nie znaleziono ceny w Redis")
        return float(price) if price else None

    async def set_cached_price(self, key: str, value: Decimal, ttl: int = 60) -> None:
        """Zapisuje wartość w Redis."""
        redis = await get_redis()
        print(f"Połączenie z Redis: {redis}")  # Debugowanie
        await redis.set(key, float(value), ex=ttl)
        print(f"Zapisano cenę {value} w Redis dla {key}")  # Debugowanie
