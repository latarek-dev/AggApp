from decimal import Decimal
from typing import List, Dict, Any, Optional
from config import camelot_abi, w3
from interfaces import IPairPriceService

class CamelotService(IPairPriceService):
    """Serwis pobierający ceny z puli Camelot."""

    def get_pair_price(self, pool_address: str, token_decimals: tuple, dex_abi: List[Dict[str, Any]] = camelot_abi) -> tuple[Decimal, Decimal]:
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=dex_abi)
            global_state = pool_contract.functions.globalState().call()
            # Debugowanie: Sprawdzamy wartość global_state przed przeliczeniem
            print(f"global_state: {global_state}")
            decimals_token, decimals_base = token_decimals
            sqrt_price = Decimal(global_state[0]) / Decimal(2 ** 96)
            price = sqrt_price ** 2

            # Debugowanie: Sprawdzamy wynik ceny po przekształceniu
            print(f"Price after transforming sqrtPrice: {price}")
            # Dostosowanie ceny względem różnicy decymalnych
            if decimals_token > decimals_base:
                price = price / Decimal(10 ** (decimals_token - decimals_base))
            else:
                price = price * Decimal(10 ** (decimals_base - decimals_token))

            # Debugowanie: Sprawdzamy wartość ceny po dostosowaniu
            print(f"Adjusted price: {price}")
            inverse_price = Decimal(1) / price if price > 0 else Decimal(0)
            return price, inverse_price

        except Exception as e:
            print(f"Błąd Camelot {pool_address}: {e}")
            return None, None

