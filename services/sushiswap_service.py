from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from interfaces import IPairPriceService
from config import sushiswap_abi, w3
from price_calculation import uniswap_calculation

class SushiswapService(IPairPriceService):
    """Serwis pobierający ceny z Sushiswap V3."""

    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]] = sushiswap_abi) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Pobiera cenę pary z Sushiswap V3."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
            slot0_data = pool_contract.functions.slot0().call()
            decimals_token, decimals_base = token_decimals
            price, inverse_price = uniswap_calculation(decimals_token, decimals_base, slot0_data)

            return price, inverse_price

        except Exception as e:
            print(f"Błąd Sushiswap {pool_address}: {e}")
            return None, None

