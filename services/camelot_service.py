from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from config import camelot_abi, erc20_abi, w3
from interfaces import IPairPriceService
from price_calculation import camelot_calculation
from liquidity_calculation import calculate_liquidity
from web3 import Web3

class CamelotService(IPairPriceService):
    """Serwis pobierający ceny z puli Camelot."""
    abi = camelot_abi

    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)
            global_state = pool_contract.functions.globalState().call()
            decimals_base, decimals_token = token_decimals
            price, inverse_price = camelot_calculation(decimals_token, decimals_base, global_state)

            return price, inverse_price

        except Exception as e:
            print(f"Błąd Camelot {pool_address}: {e}")
            return None, None


    def get_liquidity(self, pool_address: str, token_addresses, token_decimals: Tuple[int, int], prices: dict) -> Optional[Decimal]:
        """Mockowa płynność dla Camelot (do zastąpienia, jeśli znajdziesz prawdziwe źródło)."""
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
        """Mockowa stała opłata transakcyjna dla Camelot."""
        try:
            # Przykład: Camelot często ma fee 0.2% (0.002)
            tx_cost = Decimal('0.002')
            return tx_cost

        except Exception as e:
            print(f"Błąd Camelot przy obliczaniu kosztu transakcji {pool_address}: {e}")
            return None