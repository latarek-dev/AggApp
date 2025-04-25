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

    def get_pool_addresses(self, dex_service, pool_address: str) -> List[str]:
        pool_contract = w3.eth.contract(address=pool_address, abi=dex_service.abi)
        token0 = pool_contract.functions.token0().call().lower()
        token1 = pool_contract.functions.token1().call().lower()

        token0_data = self.get_token_by_address(token0)
        token1_data = self.get_token_by_address(token1)

        if token0_data and token1_data:
            return [token0, token1]
        return []
