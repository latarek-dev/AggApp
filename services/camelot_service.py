from decimal import Decimal
from typing import List, Dict, Any, Optional
from config import camelot_abi, w3
from interfaces import IPairPriceService
from price_calculation import camelot_calculation

class CamelotService(IPairPriceService):
    """Serwis pobierający ceny z puli Camelot."""

    def get_pair_price(self, pool_address: str, token_decimals: tuple, dex_abi: List[Dict[str, Any]] = camelot_abi) -> tuple[Decimal, Decimal]:
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
            global_state = pool_contract.functions.globalState().call()
            decimals_token, decimals_base = token_decimals
            price, inverse_price = camelot_calculation(decimals_token, decimals_base, global_state)

            return price, inverse_price

        except Exception as e:
            print(f"Błąd Camelot {pool_address}: {e}")
            return None, None

