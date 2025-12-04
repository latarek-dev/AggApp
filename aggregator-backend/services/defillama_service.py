import requests
import time
from typing import Optional, Dict, List
from decimal import Decimal

class DefiLlamaService:
    """Główny serwis cenowy - ceny z DefiLlama."""

    BASE_URL = "https://coins.llama.fi/prices/current"
    CHAIN = "arbitrum"

    def __init__(self, chain: str = "arbitrum"):
        self.CHAIN = chain

    def _format_key(self, token_address: str) -> str:
        return f"{self.CHAIN}:{token_address.lower()}"

    def get_price(self, token_address: str) -> Optional[Decimal]:
        """Cena pojedynczego tokena."""
        key = self._format_key(token_address)
        url = f"{self.BASE_URL}/{key}"

        for _ in range(3):
            try:
                resp = requests.get(url, timeout=6)
                resp.raise_for_status()
                data = resp.json().get("coins", {})
                price = data.get(key, {}).get("price")
                if price is None:
                    return None
                return Decimal(str(price))
            except requests.exceptions.RequestException as e:
                print(f"DefiLlama error: {e}, ponawiam próbę...")
                time.sleep(1)
        return None
        
    def get_prices_batch(self, token_addresses: List[str]) -> Dict[str, Optional[Decimal]]:
        """Batch request dla wielu tokenów."""
        if not token_addresses:
            return {}

        keys = ",".join(self._format_key(addr) for addr in token_addresses)
        url = f"{self.BASE_URL}/{keys}"

        for _ in range(3):
            try:
                resp = requests.get(url, timeout=6)
                resp.raise_for_status()
                coins = resp.json().get("coins", {})
                out: Dict[str, Optional[Decimal]] = {}
                for addr in token_addresses:
                    k = self._format_key(addr)
                    price = coins.get(k, {}).get("price")
                    out[addr] = Decimal(str(price)) if price is not None else None
                return out
            except requests.exceptions.RequestException as e:
                print(f"DefiLlama batch error: {e}, ponawiam próbę...")
                time.sleep(1)

        return {addr: None for addr in token_addresses}