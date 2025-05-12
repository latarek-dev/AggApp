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

    def get_liquidity(self, pool_address: str, token_addresses, token_decimals: Tuple[int, int], prices: dict) -> Optional[Tuple[Decimal, Decimal]]:
        """Pobiera płynność z puli Uniswap V3."""
        try:
            token0_address, token1_address = token_addresses
            decimals0, decimals1 = token_decimals

            token0_contract = w3.eth.contract(address=Web3.to_checksum_address(token0_address), abi=erc20_abi)
            token1_contract = w3.eth.contract(address=Web3.to_checksum_address(token1_address), abi=erc20_abi)

            balance0 = token0_contract.functions.balanceOf(pool_address).call()
            balance1 = token1_contract.functions.balanceOf(pool_address).call()

            """
            if token0_address not in prices or token1_address not in prices:
                print(f"Brak ceny dla tokenów: {[a for a in [token0_address, token1_address] if a not in prices]}")
                return None

            price0 = Decimal(prices[token0_address])
            price1 = Decimal(prices[token1_address])

            total_liquidity = calculate_liquidity(balance0, balance1, decimals0, decimals1, price0, price1)
            """

            balance0_normalized = Decimal(balance0) / (10 ** decimals0)
            balance1_normalized = Decimal(balance1) / (10 ** decimals1)

            return balance0_normalized, balance1_normalized

        except Exception as e:
            print(f"Błąd Uniswap przy pobieraniu płynności {pool_address}: {e}")
            return None

    def get_dex_fee_percent(self, pool_address: str) -> Optional[Decimal]:
        """Zwraca fee z puli Uniswap V3 w formacie dziesiętnym (np. 0.003 dla 0.3%)."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)
            fee_basis_points = pool_contract.functions.fee().call()
            return Decimal(fee_basis_points) / Decimal(1_000_000)
        except Exception as e:
            print(f"Błąd przy pobieraniu fee z Uniswap {pool_address}: {e}")
            return None

    def get_gas_cost_usd(self, dex_fee: Optional[Decimal], liquidity: float, eth_price: Decimal) -> Optional[Decimal]:
        """Szacuje koszt gazu w USD na podstawie opłaty puli i płynności."""
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

            gas_price_wei = w3.eth.gas_price
            print("gas price wei", gas_price_wei)
            gas_price_eth = Web3.from_wei(gas_price_wei, 'ether')
            
            gas_cost_eth = Decimal(gas_price_eth) * Decimal(gas_used)
            gas_cost_usd = gas_cost_eth * eth_price

            print(f"Fee: {dex_fee}, Liquidity: {liquidity}, Gas used: {gas_used}, Gas cost: {gas_cost_usd:.5f} USD")
            return gas_cost_usd
        except Exception as e:
            print(f"Błąd przy obliczaniu gas cost dla Uniswap: {e}")
            return None

    def get_transaction_cost(self, pool_address: str, token_from_address: str, liquidity: float, eth_price: Decimal) -> Tuple[Optional[Decimal], Optional[Decimal]]:
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

    def get_slippage(self, amount_in: Decimal, amount_out: Decimal, liquidity: Tuple[Decimal, Decimal], is_token0_from: bool) -> Optional[Decimal]:
        """
        Szacuje slippage na podstawie ilości wejściowej i sald tokenów w puli.

        Args:
            amount_in: Ilość tokenów wejściowych (token_from) w jednostkach dziesiętnych.
            liquidity: Krotka (balance0, balance1) w jednostkach dziesiętnych.
            is_token0_from: Czy token_from to token0 w puli (True) czy token1 (False).

        Returns:
            Slippage jako liczba dziesiętna (np. 0.005 dla 0.5%).
        """
        try:
            # Konwersja na Decimal, jeśli nie są już tego typu
            amount_in = Decimal(amount_in)
            amount_out = Decimal(amount_out)
            print("amount_in", amount_in)
            print("amount_out (żądane):", amount_out)
            print("liquidity krotka balansy", liquidity)
            if liquidity is None or (liquidity[0] == 0 and liquidity[1] == 0):
                print("Brak płynności - nie można obliczyć slippage.")
                return None

            reserve_in = liquidity[0] if is_token0_from else liquidity[1]
            reserve_out = liquidity[1] if is_token0_from else liquidity[0]
            reserve_in, reserve_out = reserve_in, reserve_out

            if reserve_in == 0 or reserve_out == 0:
                print("Brak płynności dla jednego z tokenów.")
                return None

            # Zabezpieczenie: żądany amount_out nie może przekraczać puli
            if amount_out >= reserve_out:
                print("Zbyt duża kwota wyjściowa w stosunku do płynności.")
                slippage = Decimal('0.999')  # Maksymalny slippage (99.9%)
                return slippage

            # Krok 1: Użyj amount_out jako expected_amount_out
            expected_amount_out = amount_out

            # Krok 2: Rzeczywisty amount_out z AMM (bez opłaty)
            new_reserve_in = reserve_in + amount_in
            new_reserve_out = (reserve_in * reserve_out) / new_reserve_in
            actual_amount_out = reserve_out - new_reserve_out
            print("Rzeczywisty amount_out (z AMM):", actual_amount_out)

            # Zabezpieczenie: jeśli actual_amount_out przekracza pulę, ustaw maksymalny slippage
            if actual_amount_out >= reserve_out:
                print("Rzeczywisty amount_out przekracza rezerwę w puli!")
                slippage = Decimal('0.999')
                return slippage

            slippage = (expected_amount_out - actual_amount_out) / expected_amount_out
            print("Obliczony slippage:", slippage)

            if slippage < 0:
                print("Uwaga: Negatywny slippage, ustawiam na 0.")
                slippage = Decimal('0')

            return slippage

        except Exception as e:
            print(f"Błąd przy obliczaniu slippage: {e}")
            return None