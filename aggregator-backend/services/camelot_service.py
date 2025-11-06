from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from config import camelot_abi, w3
from token_manager import TokenManager
from web3 import Web3
from pools_config import TOKENS
from .base_dex_service import BaseDexService
from .calculation_service import mid_price_from_univ3_sqrt

token_manager = TokenManager(TOKENS)

QUOTER_ADDRESS = Web3.to_checksum_address("0x0Fc73040b26E9bC8514fA028D998E73A254Fa76E")
quoter_abi = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "address", "name": "tokenOut", "type": "address"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint160", "name": "limitSqrtPrice", "type": "uint160"}
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint16", "name": "fee", "type": "uint16"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

class CamelotService(BaseDexService):
    """Camelot V3 - dynamiczne fee z globalState."""
    abi = camelot_abi

    def get_dex_fee_percent(self, pool_address: str, token_from_address: str) -> Optional[Decimal]:
        """Fee z globalState (feeZto lub feeOtz w zależności od kierunku)."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)

            token0 = pool_contract.functions.token0().call()
            token1 = pool_contract.functions.token1().call()

            global_state = pool_contract.functions.globalState().call()
            print("global_state", global_state)
            _, _, feeZto, feeOtz, *_ = global_state

            if token_from_address.lower() == token0.lower():
                fee_basis_points = feeZto
            elif token_from_address.lower() == token1.lower():
                fee_basis_points = feeOtz
            else:
                print(f"Token {token_from_address} nie pasuje do token0 ani token1.")
                return None

            return Decimal(fee_basis_points) / Decimal(1_000_000)
        except Exception as e:
            print(f"Błąd przy pobieraniu fee z Camelot {pool_address}: {e}")
            return None

    def get_mid_price(self, pool_address, token_from, token_to, token_decimals, token_addresses=None) -> Optional[Decimal]:
        """Mid-price z globalState[0] (sqrtPriceX96)."""
        try:
            pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            
            if token_addresses and len(token_addresses) == 2:
                token0 = token_addresses[0].lower()
            else:
                token0 = pool.functions.token0().call().lower()
            
            dec0, dec1 = token_decimals
            is0_in = token_manager.get_address_by_symbol(token_from).lower() == token0
            
            global_state = pool.functions.globalState().call()
            sqrt_x96 = global_state[0]
            
            return mid_price_from_univ3_sqrt(sqrt_x96, dec0, dec1, is0_in)
        except Exception as e:
            print(f"Błąd mid_price Camelot: {e}")
            return None

    def quote_exact_in(self, pool_address, token_from, token_to, amount_in, token_decimals, token_addresses=None, pool_fee=None, pair=None) -> Optional[Decimal]:
        """Quote z Camelot Quoter (zwraca amountOut + feeUsed)."""
        try:
            pool   = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            quoter = w3.eth.contract(address=QUOTER_ADDRESS, abi=quoter_abi)

            token_in_addr  = Web3.to_checksum_address(token_manager.get_address_by_symbol(token_from))
            token_out_addr = Web3.to_checksum_address(token_manager.get_address_by_symbol(token_to))

            if token_addresses and len(token_addresses) == 2:
                token0 = token_addresses[0].lower()
            else:
                token0 = pool.functions.token0().call().lower()
            
            dec0, dec1 = token_decimals
            is0_in = token_in_addr.lower() == token0
            dec_in  = dec0 if is0_in else dec1
            dec_out = dec1 if is0_in else dec0

            amount_in_wei = int(amount_in * Decimal(10 ** dec_in))
            
            print(f"Camelot Quoter: token_in={token_from} ({dec_in} dec), amount_in={amount_in_wei}")
            
            # Camelot Quoter zwraca (amountOut, feeUsed)
            amount_out_wei, _fee_used = quoter.functions.quoteExactInputSingle(
                token_in_addr, token_out_addr, amount_in_wei, 0
            ).call()
            
            print(f"Camelot response: amount_out_wei={amount_out_wei}")
            
            return Decimal(amount_out_wei) / Decimal(10 ** dec_out)
        except Exception as e:
            print(f"Błąd quote_exact_in Camelot: {e}")
            return None

    def get_transaction_cost(self, pool_address: str, token_from_address: str, liquidity: float, eth_price: Decimal) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Zwraca podsumowanie kosztów transakcji: fee + gaz w USD."""
        try:
            # Camelot wymaga token_from_address dla get_dex_fee_percent
            dex_fee = self.get_dex_fee_percent(pool_address, token_from_address)
            gas_cost = self.get_gas_cost_usd(dex_fee, liquidity, eth_price=eth_price)

            if dex_fee is None or gas_cost is None:
                return None, None

            return dex_fee, gas_cost

        except Exception as e:
            print(f"Błąd przy tworzeniu podsumowania kosztów Camelot: {e}")
            return None, None