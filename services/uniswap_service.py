from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from interfaces import IPairPriceService
from config import uniswap_abi, w3
from price_calculation import uniswap_calculation

class UniswapService(IPairPriceService):
    """Serwis pobierający ceny z Uniswap V3."""

    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]] = uniswap_abi) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Pobiera cenę pary z Uniswap V3."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
            slot0_data = pool_contract.functions.slot0().call()
            decimals_token, decimals_base = token_decimals
            price, inverse_price = uniswap_calculation(decimals_token, decimals_base, slot0_data)

            return price, inverse_price

        except Exception as e:
            print(f"Błąd Uniswap {pool_address}: {e}")
            return None, None

    def get_liquidity(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]] = uniswap_abi) -> Optional[Decimal]:
        """Pobiera płynność z puli Uniswap V3."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
            liquidity = pool_contract.functions.liquidity().call()

            # Zakładamy, że używamy średniej precyzji z obu tokenów do skalowania (można inaczej)
            avg_decimals = sum(token_decimals) / 2
            return Decimal(liquidity) / (10 ** int(avg_decimals))

        except Exception as e:
            print(f"Błąd Uniswap przy pobieraniu płynności {pool_address}: {e}")
            return None

    def get_transaction_cost(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]] = uniswap_abi) -> Optional[Decimal]:
        """Szacuje koszt transakcji na Uniswapie V3 (np. opłata 0.3% lub 0.05% w zależności od puli)."""
        try:
            # Przykładowa stała opłata transakcyjna (np. 0.3% = 0.003)
            # W przyszłości możesz pobierać fee z kontraktu (np. z pola `fee`)
            tx_cost = Decimal('0.003')
            return tx_cost

        except Exception as e:
            print(f"Błąd Uniswap przy obliczaniu kosztu transakcji {pool_address}: {e}")
            return None
