from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Tuple

class IPairPriceService(ABC):

    """Interfejs dla serwisów pobierających ceny par tokenów."""

    @abstractmethod
    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        pass