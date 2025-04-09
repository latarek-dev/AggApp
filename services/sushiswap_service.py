from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from interfaces import IPairPriceService
from config import sushiswap_abi, w3

class SushiswapService(IPairPriceService):
    """Serwis pobierający ceny z Sushiswap V3."""

    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int], dex_abi: List[Dict[str, Any]] = sushiswap_abi) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Pobiera cenę pary z Sushiswap V3."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
            slot0_data = pool_contract.functions.slot0().call()
            sqrt_price_x96 = slot0_data[0]
            sqrt_price = Decimal(sqrt_price_x96) / Decimal(2 ** 96)
            price_in_base = sqrt_price ** 2
            decimals_token, decimals_base = token_decimals
            if decimals_token > decimals_base:
                adjusted_price = price_in_base / Decimal(10 ** (decimals_token - decimals_base))
            else:
                adjusted_price = price_in_base * Decimal(10 ** (decimals_base - decimals_token))
            inverse_price = Decimal(1) / adjusted_price if adjusted_price != 0 else Decimal(0)
            return adjusted_price, inverse_price

        except Exception as e:
            print(f"Błąd Sushiswap {pool_address}: {e}")
            return None, None

