import requests
import time
import random
from typing import Optional, Dict, List
from decimal import Decimal
from interfaces import ISingleTokenPriceService

class CoinGeckoService(ISingleTokenPriceService):
    """Fallback serwis cenowy - CoinGecko (gdy DefiLlama nie zwróci cen). Circuit Breaker wyłącza API po 3 błędach na 60s."""

    BASE_URL = "https://api.coingecko.com/api/v3/simple/token_price/arbitrum-one"
    PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"
    
    WETH_ADDRESS = "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
    
    _circuit_breaker = {
        'failure_count': 0,
        'last_failure_time': 0,
        'is_open': False,
        'open_until': 0
    }
    
    FAILURE_THRESHOLD = 3
    CIRCUIT_TIMEOUT = 60
    FAILURE_WINDOW = 30

    def get_price(self, token_address: str) -> Optional[Decimal]:
        """Pobiera cenę tokena w USD."""
        token_address = token_address.lower()
        url = f"{self.BASE_URL}?contract_addresses={token_address}&vs_currencies=usd"
        for attempt in range(2):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                return Decimal(data.get(token_address, {}).get("usd", 0))

            except requests.exceptions.RequestException as e:
                if attempt < 1:
                    print(f"Błąd CoinGecko: {e}, ponawiam próbę...")
                    time.sleep(0.1)
                else:
                    print(f"Błąd CoinGecko: {e}")
                    return None

        return None

    def _check_circuit_breaker(self) -> bool:
        """True = circuit otwarty (pomiń API), False = circuit zamknięty (próbuj)."""
        current_time = time.time()
        
        if self._circuit_breaker['is_open']:
            if current_time >= self._circuit_breaker['open_until']:
                print("Circuit Breaker: Reset - próbuję CoinGecko ponownie")
                self._circuit_breaker['is_open'] = False
                self._circuit_breaker['failure_count'] = 0
                return False
            else:
                remaining = int(self._circuit_breaker['open_until'] - current_time)
                print(f"Circuit Breaker OTWARTY - pomijam CoinGecko (reset za {remaining}s)")
                return True
        
        if self._circuit_breaker['last_failure_time'] > 0:
            if current_time - self._circuit_breaker['last_failure_time'] > self.FAILURE_WINDOW:
                self._circuit_breaker['failure_count'] = 0
        
        return False
    
    def _record_failure(self):
        """Zlicza błędy i otwiera circuit po przekroczeniu progu."""
        current_time = time.time()
        self._circuit_breaker['failure_count'] += 1
        self._circuit_breaker['last_failure_time'] = current_time
        
        if self._circuit_breaker['failure_count'] >= self.FAILURE_THRESHOLD:
            self._circuit_breaker['is_open'] = True
            self._circuit_breaker['open_until'] = current_time + self.CIRCUIT_TIMEOUT
            print(f"Circuit Breaker OTWARTY - {self._circuit_breaker['failure_count']} błędów")
    
    def _record_success(self):
        """Resetuje licznik błędów po sukcesie."""
        if self._circuit_breaker['failure_count'] > 0:
            print(f"Circuit Breaker: Reset licznika ({self._circuit_breaker['failure_count']} -> 0)")
            self._circuit_breaker['failure_count'] = 0
    
    def get_prices_batch(self, token_addresses: List[str]) -> Dict[str, Optional[Decimal]]:
        """Batch request. WETH przez ID 'ethereum', inne przez adresy. Circuit Breaker po 3 błędach."""
        if not token_addresses:
            return {}
        
        if self._check_circuit_breaker():
            return {addr: None for addr in token_addresses}
        
        weth_addrs = []
        other_addrs = []
        
        for addr in token_addresses:
            if addr.lower() == self.WETH_ADDRESS.lower():
                weth_addrs.append(addr)
            else:
                other_addrs.append(addr)
        
        result = {}
        has_any_success = False
        
        if weth_addrs:
            weth_price = self._get_weth_price()
            for addr in weth_addrs:
                result[addr] = weth_price
            if weth_price is not None:
                has_any_success = True
        
        if other_addrs:
            other_prices = self._get_prices_by_address(other_addrs)
            result.update(other_prices)
            if any(price is not None for price in other_prices.values()):
                has_any_success = True
        
        if has_any_success:
            self._record_success()
        else:
            self._record_failure()
        
        return result
    
    def _get_weth_price(self) -> Optional[Decimal]:
        """WETH przez ID 'ethereum' (adres nie działa w CoinGecko)."""
        url = f"{self.PRICE_URL}?ids=ethereum&vs_currencies=usd"
        
        delay = 0.1
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                price = data.get("ethereum", {}).get("usd")
                if price:
                    print(f"CoinGecko WETH (ethereum): ${price}")
                    return Decimal(str(price))
                return None
                
            except requests.exceptions.HTTPError as e:
                if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    if attempt < max_attempts - 1:
                        jitter = random.uniform(0, 0.1)
                        sleep_time = delay + jitter
                        print(f"CoinGecko 429 (WETH) - czekam {sleep_time:.2f}s")
                        time.sleep(sleep_time)
                        delay *= 2
                        continue
                print(f"CoinGecko 429 (WETH) - przechodzę do fallback")
                return None
                
            except requests.exceptions.RequestException as e:
                print(f"Błąd CoinGecko WETH: {e}")
                return None
        
        return None
    
    def _get_prices_by_address(self, token_addresses: List[str]) -> Dict[str, Optional[Decimal]]:
        """Ceny przez adresy kontraktów z exponential backoff (szybki fallback przy 429)."""
        if not token_addresses:
            return {}
        
        addresses = ",".join(addr.lower() for addr in token_addresses)
        url = f"{self.BASE_URL}?contract_addresses={addresses}&vs_currencies=usd"
        
        delay = 0.1
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                data = response.json()
                print(f"CoinGecko batch ({len(token_addresses)} tokenów)")
                
                result = {}
                for addr in token_addresses:
                    price_data = data.get(addr.lower(), {}).get("usd")
                    result[addr] = Decimal(str(price_data)) if price_data else None
                
                return result
                
            except requests.exceptions.HTTPError as e:
                if hasattr(e.response, 'status_code') and e.response.status_code == 429:
                    if attempt < max_attempts - 1:
                        jitter = random.uniform(0, 0.1)
                        sleep_time = delay + jitter
                        print(f"CoinGecko 429 - czekam {sleep_time:.2f}s przed próbą {attempt + 2}")
                        time.sleep(sleep_time)
                        delay *= 2
                        continue
                    print(f"CoinGecko 429 - przechodzę do fallback po {max_attempts} próbach")
                    return {addr: None for addr in token_addresses}
                print(f"Błąd CoinGecko batch: {e}")
                return {addr: None for addr in token_addresses}
                
            except requests.exceptions.RequestException as e:
                print(f"Błąd CoinGecko batch: {e}")
                return {addr: None for addr in token_addresses}
        
        return {addr: None for addr in token_addresses}