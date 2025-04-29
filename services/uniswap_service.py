from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from interfaces import IPairPriceService
from config import uniswap_abi, erc20_abi, w3
from price_calculation import uniswap_calculation
from liquidity_calculation import calculate_liquidity
from web3 import Web3

class UniswapService(IPairPriceService):
    """Serwis pobierający ceny z Uniswap V3."""
    abi = uniswap_abi

    def get_pair_price(self, pool_address: str, token_decimals: Tuple[int, int]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Pobiera cenę pary z Uniswap V3."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)
            slot0_data = pool_contract.functions.slot0().call()
            decimals_base, decimals_token = token_decimals
            price, inverse_price = uniswap_calculation(decimals_token, decimals_base, slot0_data)

            return price, inverse_price

        except Exception as e:
            print(f"Błąd Uniswap {pool_address}: {e}")
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

    def get_dex_fee_percent(self, pool_address: str) -> Optional[Decimal]:
        """Zwraca fee z puli Uniswap V3 w formacie dziesiętnym (np. 0.003 dla 0.3%)."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)
            fee_basis_points = pool_contract.functions.fee().call()  # np. 3000 -> 0.003
            return Decimal(fee_basis_points) / Decimal(1_000_000)
        except Exception as e:
            print(f"Błąd przy pobieraniu fee z Uniswap {pool_address}: {e}")
            return None

    def get_gas_cost_usd(self, dex_fee: Optional[Decimal], liquidity: float, eth_price: Decimal) -> Optional[Decimal]:
        """Szacuje koszt gazu w USD na podstawie opłaty puli i płynności."""
        try:
            # Określ szacunkowe zużycie gazu na podstawie dex_fee
            if dex_fee is None:
                gas_used = 140_000  # Domyślna wartość
            elif dex_fee == Decimal('0.0001'):  # 0.01% (np. USDT/DAI)
                gas_used = 110_000
            elif dex_fee == Decimal('0.0005'):  # 0.05%
                gas_used = 120_000
            elif dex_fee == Decimal('0.003'):   # 0.3%
                gas_used = 140_000
            elif dex_fee == Decimal('0.01'):    # 1%
                gas_used = 160_000
            else:
                gas_used = 140_000  # Domyślna dla nieznanych opłat

            # Zwiększ gaz dla pul o niskiej płynności
            if liquidity < 100_000:
                gas_used += 15_000  # Mniejsza korekta po blobs

            gas_price_wei = max(w3.eth.gas_price, 10_000_000)  # np. 35 gwei
            print("gas price wei", gas_price_wei)
            gas_price_eth = Web3.from_wei(gas_price_wei, 'ether')
            
            gas_cost_eth = Decimal(gas_price_eth) * Decimal(gas_used)
            gas_cost_usd = gas_cost_eth * eth_price

            print(f"Fee: {dex_fee}, Liquidity: {liquidity}, Gas used: {gas_used}, Gas cost: {gas_cost_usd:.5f} USD")
            return gas_cost_usd
        except Exception as e:
            print(f"Błąd przy obliczaniu gas cost dla Uniswap: {e}")
            return None

    def get_transaction_cost(self, pool_address: str, liquidity: float, eth_price: Decimal) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Zwraca podsumowanie kosztów transakcji: fee + gaz w USD."""
        try:
            dex_fee = self.get_dex_fee_percent(pool_address)
            gas_cost = self.get_gas_cost_usd(dex_fee, liquidity, eth_price=eth_price)

            if dex_fee is None or gas_cost is None:
                return None

            return dex_fee, gas_cost

        except Exception as e:
            print(f"Błąd przy tworzeniu podsumowania kosztów Uniswap: {e}")
            return None
