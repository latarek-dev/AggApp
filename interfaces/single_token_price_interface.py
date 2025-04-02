from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

class ISingleTokenPriceService(ABC):
    """Interfejs dla serwisów pobierających cenę pojedynczego tokena w USD."""

    @abstractmethod
    def get_price(self, token_id: str) -> Optional[Decimal]:
        """Pobiera cenę tokena w USD."""
        pass
