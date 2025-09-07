from typing import Optional
from decimal import Decimal
from interfaces import ICacheService
from .redis_service import redis_service

class RedisCacheService(ICacheService):
    """Serwis obsługujący cache w Redis."""

    async def get_cached_price(self, key: str) -> Optional[float]:
        """Pobiera wartość z Redis."""
        price = await redis_service.get(key)
        if price:
            print(f"Znaleziono cenę w Redis: {price}")
        else:
            print(f"Nie znaleziono ceny w Redis")
        return float(price) if price else None

    async def set_cached_price(self, key: str, value: Decimal, ttl: int = 60) -> None:
        """Zapisuje wartość w Redis."""
        success = await redis_service.set(key, float(value), ex=ttl)
        if success:
            print(f"Zapisano cenę {value} w Redis dla {key}")
        else:
            print(f"Błąd podczas zapisywania ceny {value} w Redis dla {key}")
