from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

class ICacheService(ABC):
    """Interfejs dla serwisów cache."""
    
    @abstractmethod
    async def get_cached_price(self, key: str) -> Optional[float]:
        pass
    
    @abstractmethod
    async def set_cached_price(self, key: str, value: Decimal, ttl: int = 60) -> None:
        pass
    