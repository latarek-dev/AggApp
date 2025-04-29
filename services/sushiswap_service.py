from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from interfaces import IPairPriceService
from config import sushiswap_abi, erc20_abi, w3
from price_calculation import uniswap_calculation
from liquidity_calculation import calculate_liquidity
from web3 import Web3

class SushiswapService(IPairPriceService):
    """Serwis pobierający ceny z Sushiswap V3."""
    abi = sushiswap_abi

    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Pobiera cenę pary z Sushiswap V3."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)
            slot0_data = pool_contract.functions.slot0().call()
            decimals_base, decimals_token = token_decimals
            price, inverse_price = uniswap_calculation(decimals_token, decimals_base, slot0_data)

            return price, inverse_price

        except Exception as e:
            print(f"Błąd Sushiswap {pool_address}: {e}")
            return None, None

    def get_liquidity(self, pool_address: str, token_addresses, token_decimals: Tuple[int, int], prices: dict) -> Optional[Decimal]:
        """Pobiera płynność z puli Uniswap V3."""
        try:
            token0_address, token1_address = token_addresses
            decimals0, decimals1 = token_decimals

            # Tworzymy kontrakty ERC20
            token0_contract = w3.eth.contract(address=Web3.to_checksum_address(token0_address), abi=erc20_abi)
            token1_contract = w3.eth.contract(address=Web3.to_checksum_address(token1_address), abi=erc20_abi)

            # Pobieramy balanceOf dla adresu puli
            balance0 = token0_contract.functions.balanceOf(pool_address).call()
            balance1 = token1_contract.functions.balanceOf(pool_address).call()

            if token0_address not in prices or token1_address not in prices:
                print(f"Brak ceny dla tokenów: {[a for a in [token0_address, token1_address] if a not in prices]}")
                return None

            price0 = Decimal(prices[token0_address])
            price1 = Decimal(prices[token1_address])

            total_liquidity = calculate_liquidity(balance0, balance1, decimals0, decimals1, price0, price1)

            # Można też zwrócić tuple, ale tu np. suma jako przybliżona płynność
            return total_liquidity

        except Exception as e:
            print(f"Błąd Uniswap przy pobieraniu płynności {pool_address}: {e}")
            return None

    def get_transaction_cost(self, pool_address: str, token_decimals: Tuple[int, int]) -> Optional[Decimal]:
        """Szacuje koszt transakcji na Uniswapie V3 (np. opłata 0.3% lub 0.05% w zależności od puli)."""
        try:
            # Przykładowa stała opłata transakcyjna (np. 0.3% = 0.003)
            # W przyszłości możesz pobierać fee z kontraktu (np. z pola `fee`)
            tx_cost = Decimal('0.003')
            return tx_cost

        except Exception as e:
            print(f"Błąd Uniswap przy obliczaniu kosztu transakcji {pool_address}: {e}")
            return None
