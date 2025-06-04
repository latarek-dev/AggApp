from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from interfaces import IPairPriceService
from config import uniswap_abi, erc20_abi, w3
from price_calculation import uniswap_calculation
from liquidity_calculation import calculate_liquidity
from token_manager import TokenManager
from web3 import Web3
from pools_config import TOKENS

token_manager = TokenManager(TOKENS)
QUOTER_ADDRESS = Web3.to_checksum_address("0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6")
quoter_abi = [
    {
      "inputs":[
        {"internalType":"address","name":"tokenIn","type":"address"},
        {"internalType":"address","name":"tokenOut","type":"address"},
        {"internalType":"uint24","name":"fee","type":"uint24"},
        {"internalType":"uint256","name":"amountIn","type":"uint256"},
        {"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}
      ],
      "name":"quoteExactInputSingle",
      "outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],
      "stateMutability":"view","type":"function"
    }
]

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

    def get_slippage(
        self,
        pool_address: str,
        amount_in: Decimal,
        token_from: str,
        token_to: str,
        token_decimals: Tuple[int, int],
    ) -> Optional[Dict[str, Decimal]]:
        """
        Szacuje slippage za pomocą Quoter V3, ale najpierw sprawdza dostępność płynności:
        - amount_out   : ile token_to otrzymasz,
        - slippage     : (ideal_out - actual_out) / ideal_out,
        - price_before : początkowy kurs token_to/token_from.
        """
        try:
            # 1) Pool + Quoter
            pool   = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            quoter = w3.eth.contract(address=QUOTER_ADDRESS, abi=quoter_abi)

            # 2) Fee tier
            fee_tier = pool.functions.fee().call()

            # 3) Adresy tokenów i kierunek
            token0_addr = pool.functions.token0().call()
            token1_addr = pool.functions.token1().call()
            dec0, dec1 = token_decimals
            is0 = (token_manager.get_address_by_symbol(token_from).lower() == token0_addr.lower())
            dec_in, dec_out = (dec0, dec1) if is0 else (dec1, dec0)

            # 4) Sprawdzenie rezerw w wei
            erc0 = w3.eth.contract(address=Web3.to_checksum_address(token0_addr), abi=erc20_abi)
            erc1 = w3.eth.contract(address=Web3.to_checksum_address(token1_addr), abi=erc20_abi)
            bal0 = erc0.functions.balanceOf(pool_address).call()
            bal1 = erc1.functions.balanceOf(pool_address).call()
            reserve_in_wei  = bal0 if is0 else bal1
            reserve_out_wei = bal1 if is0 else bal0

            # 5) amount_in → wei i walidacja
            amount_in_wei = int(amount_in * Decimal(10 ** dec_in))
            if amount_in_wei > reserve_in_wei:
                print(f"Brak płynności: żądane {amount_in_wei} > rezerwa {reserve_in_wei}")
                return None

            # 6) Quoter
            amount_out_wei = quoter.functions.quoteExactInputSingle(
                Web3.to_checksum_address(token_manager.get_address_by_symbol(token_from)),
                Web3.to_checksum_address(token_manager.get_address_by_symbol(token_to)),
                fee_tier,
                amount_in_wei,
                0
            ).call()
            if amount_out_wei > reserve_out_wei:
                print(f"Brak płynności wyjścia: {amount_out_wei} > {reserve_out_wei}")
                return None

            # 7) Konwersja actual_out
            actual_out = Decimal(amount_out_wei) / Decimal(10 ** dec_out)

            # 8) Obliczenie ideal_out na podstawie slot0
            slot0 = pool.functions.slot0().call()
            sqrt_x96 = slot0[0]
            ratio_x96 = Decimal(sqrt_x96) / Decimal(2**96)
            price_chain = ratio_x96 ** 2
            scale = Decimal(10 ** (dec0 - dec1))
            price_before = price_chain * scale if is0 else (Decimal(1) / (price_chain * scale))
            ideal_out = amount_in * price_before

            # 9) Slippage
            slippage = (ideal_out - actual_out) / ideal_out if ideal_out > 0 else Decimal(0)

            return {
                "amount_out": actual_out,
                "slippage": max(slippage, Decimal(0)),
                "price_before": price_before
            }

        except Exception as e:
            print(f"Błąd get_slippage (quoter): {e}")
            return None
