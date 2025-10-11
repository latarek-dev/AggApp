from decimal import Decimal
from typing import Optional, List, Tuple
from pools_config import TOKENS
from web3 import Web3
from config import w3

class TokenManager:
    def __init__(self, tokens_data: dict):
        """
        Inicjalizuje TokenManager z danymi o tokenach.
        tokens_data: dict - słownik danych o tokenach, np. z pliku konfiguracyjnego.
        """
        self.tokens = tokens_data
        self.tokens_by_address = {v["address"].lower(): v for k, v in self.tokens.items()}

    def get_address_by_symbol(self, symbol: str) -> Optional[str]:
        token = self.tokens.get(symbol.upper())
        if token:
            return token["address"].lower()
        return None

    def get_token_by_address(self, address: str):
        """Zwraca dane tokena na podstawie adresu"""
        return self.tokens_by_address.get(address.lower())

    def get_decimals_for_pool(self, token_addresses: list) -> Tuple[int, int]:
        """Zwraca decimalsy dla pary tokenów"""
        token0_address, token1_address = token_addresses
        token0 = self.get_token_by_address(token0_address)
        token1 = self.get_token_by_address(token1_address)
        if token0 and token1:
            return token0["decimals"], token1["decimals"]
        return 0, 0

    def get_pool_addresses(self, pair: str) -> List[str]:
        """Wyprowadza adresy tokenów z nazwy pary"""
        try:
            tokens = pair.split('/')
            if len(tokens) != 2:
                return []
            
            token0_symbol, token1_symbol = tokens
            
            token0_data = self.tokens.get(token0_symbol.upper())
            token1_data = self.tokens.get(token1_symbol.upper())
            
            if not token0_data or not token1_data:
                print(f"Brak definicji dla tokenów w parze {pair}")
                return []
            
            return [token0_data["address"].lower(), token1_data["address"].lower()]
        except Exception as e:
            print(f"Błąd wyprowadzania tokenów z {pair}: {e}")
            return []
