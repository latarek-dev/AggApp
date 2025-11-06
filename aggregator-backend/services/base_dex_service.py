from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from config import erc20_abi, w3
from token_manager import TokenManager
from web3 import Web3
from pools_config import TOKENS
import time

token_manager = TokenManager(TOKENS)

_gas_price_cache = {'value': None, 'timestamp': 0}

def get_cached_gas_price():
    """Gas price z cache (60s TTL) lub blockchain."""
    current_time = time.time()
    
    if _gas_price_cache['value'] is not None and _gas_price_cache['timestamp'] + 60 > current_time:
        return _gas_price_cache['value']
    
    gas_price = w3.eth.gas_price
    _gas_price_cache['value'] = gas_price
    _gas_price_cache['timestamp'] = current_time
    
    return gas_price

class BaseDexService:
    """Bazowa klasa dla UniswapService, SushiSwapService, CamelotService."""
    
    def get_liquidity(self, pool_address: str, token_addresses, token_decimals: Tuple[int, int], prices: dict) -> Optional[Tuple[Decimal, Decimal]]:
        """Płynność puli (balanceOf dla token0 i token1)."""
        try:
            token0_address, token1_address = token_addresses
            decimals0, decimals1 = token_decimals

            token0_contract = w3.eth.contract(address=Web3.to_checksum_address(token0_address), abi=erc20_abi)
            token1_contract = w3.eth.contract(address=Web3.to_checksum_address(token1_address), abi=erc20_abi)

            balance0 = token0_contract.functions.balanceOf(pool_address).call()
            balance1 = token1_contract.functions.balanceOf(pool_address).call()

            balance0_normalized = Decimal(balance0) / (10 ** decimals0)
            balance1_normalized = Decimal(balance1) / (10 ** decimals1)

            return balance0_normalized, balance1_normalized

        except Exception as e:
            print(f"Błąd przy pobieraniu płynności {pool_address}: {e}")
            return None

    def get_gas_cost_usd(self, dex_fee: Optional[Decimal], liquidity: float, eth_price: Decimal) -> Optional[Decimal]:
        """Koszt gazu w USD (gas_used zależy od fee tier i płynności)."""
        try:
            if dex_fee is None:
                gas_used = 140_000
            elif dex_fee == Decimal('0.0001'):
                gas_used = 110_000
            elif dex_fee == Decimal('0.0005'):
                gas_used = 120_000
            elif dex_fee == Decimal('0.003'):
                gas_used = 140_000
            elif dex_fee == Decimal('0.01'):
                gas_used = 160_000
            else:
                gas_used = 140_000

            if liquidity < 100_000:
                gas_used += 15_000

            gas_price_wei = get_cached_gas_price()
            print("gas price wei", gas_price_wei)
            gas_price_eth = Web3.from_wei(gas_price_wei, 'ether')
            
            gas_cost_eth = Decimal(gas_price_eth) * Decimal(gas_used)
            gas_cost_usd = gas_cost_eth * eth_price

            print(f"Fee: {dex_fee}, Liquidity: {liquidity}, Gas used: {gas_used}, Gas cost: {gas_cost_usd:.5f} USD")
            return gas_cost_usd
        except Exception as e:
            print(f"Błąd przy obliczaniu gas cost dla {self.__class__.__name__}: {e}")
            return None

    def get_transaction_cost(self, pool_address: str, token_from_address: str, liquidity: float, eth_price: Decimal) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Zwraca (dex_fee, gas_cost_usd)."""
        try:
            dex_fee = self.get_dex_fee_percent(pool_address)
            gas_cost = self.get_gas_cost_usd(dex_fee, liquidity, eth_price=eth_price)

            if dex_fee is None or gas_cost is None:
                return None, None

            return dex_fee, gas_cost

        except Exception as e:
            print(f"Błąd przy tworzeniu podsumowania kosztów {self.__class__.__name__}: {e}")
            return None, None
