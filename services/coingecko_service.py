import requests
import time
from typing import Optional
from decimal import Decimal
from interfaces import ISingleTokenPriceService

class CoinGeckoService(ISingleTokenPriceService):
    """Serwis pobierający ceny z CoinGecko."""

    BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

    def get_price(self, token_id: str) -> Optional[Decimal]:
        """Pobiera cenę tokena w USD."""
        url = f"{self.BASE_URL}?ids={token_id}&vs_currencies=usd"
        for _ in range(3):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                return Decimal(data.get(token_id, {}).get("usd", 0))

            except requests.exceptions.RequestException as e:
                print(f"Błąd CoinGecko: {e}, ponawiam próbę...")
                time.sleep(1)

        return None