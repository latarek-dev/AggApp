from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Tuple, List, Dict, Any

class IPairPriceService(ABC):

    """Interfejs dla serwisów pobierających ceny par tokenów."""

    @abstractmethod
    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        pass

    @abstractmethod
    def get_liquidity(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]]) -> Optional[Decimal]:
        pass

    @abstractmethod
    def get_transaction_cost(self, pool_address: str, token_from_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]]) -> Optional[Decimal]:
        pass