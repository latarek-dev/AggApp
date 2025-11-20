from decimal import Decimal
from typing import Optional
from web3 import Web3
from config import sushiswap_abi, w3
from token_manager import TokenManager
from pools_config import TOKENS
from .base_dex_service import BaseDexService
from .calculation_service import mid_price_from_univ3_sqrt

token_manager = TokenManager(TOKENS)

QUOTER_V2_ADDRESS = Web3.to_checksum_address("0x0524E833cCD057e4d7A296e3aaAb9f7675964Ce1")

QUOTER_V2_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct IQuoterV2.QuoteExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceX96After", "type": "uint160"},
            {"internalType": "uint32", "name": "initializedTicksCrossed", "type": "uint32"},
            {"internalType": "uint256", "name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    { "inputs": [], "name": "factory", "outputs": [{"internalType":"address","name":"","type":"address"}],
      "stateMutability": "view", "type": "function" },
    { "inputs": [], "name": "WETH9", "outputs": [{"internalType":"address","name":"","type":"address"}],
      "stateMutability": "view", "type": "function" },
]

class SushiswapService(BaseDexService):
    abi = sushiswap_abi

    def get_dex_fee_percent(self, pool_address: str) -> Optional[Decimal]:
        try:
            pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            fee_uint24 = pool.functions.fee().call()
            return Decimal(fee_uint24) / Decimal(1_000_000)
        except Exception as e:
            print(f"Błąd fee Sushiswap {pool_address}: {e}")
            return None

    def get_mid_price(self, pool_address, token_from, token_to, token_decimals, token_addresses=None) -> Optional[Decimal]:
        try:
            pool = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            
            if token_addresses and len(token_addresses) == 2:
                token0 = token_addresses[0].lower()
            else:
                token0 = pool.functions.token0().call().lower()
            
            dec0, dec1 = token_decimals
            is0_in = token_manager.get_address_by_symbol(token_from).lower() == token0
            sqrt_x96 = pool.functions.slot0().call()[0]
            return mid_price_from_univ3_sqrt(sqrt_x96, dec0, dec1, is0_in)
        except Exception as e:
            print(f"Błąd mid_price Sushiswap: {e}")
            return None

    def quote_exact_in(self, pool_address, token_from, token_to, amount_in, token_decimals, token_addresses=None, pool_fee=None, pair=None) -> Optional[Decimal]:
        try:
            pool   = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            quoter = w3.eth.contract(address=QUOTER_V2_ADDRESS, abi=QUOTER_V2_ABI)


            if pool_fee:
                fee_tier = int(pool_fee)
            else:
                fee_tier = int(pool.functions.fee().call())

            token_in  = Web3.to_checksum_address(token_manager.get_address_by_symbol(token_from))
            token_out = Web3.to_checksum_address(token_manager.get_address_by_symbol(token_to))

            if token_addresses and len(token_addresses) == 2:
                token0 = token_addresses[0].lower()
            else:
                token0 = pool.functions.token0().call().lower()
            
            dec0, dec1 = token_decimals
            is0_in = token_in.lower() == token0
            dec_in  = dec0 if is0_in else dec1
            dec_out = dec1 if is0_in else dec0

            amount_in_wei = int(Decimal(amount_in) * (Decimal(10) ** dec_in))

            params = {
                "tokenIn": token_in,
                "tokenOut": token_out,
                "amountIn": amount_in_wei,
                "fee": fee_tier,
                "sqrtPriceLimitX96": 0,
            }

            print(f"SushiSwap Quoter: token_in={token_from} ({dec_in} dec), amount_in={amount_in_wei}")

            amount_out_wei, _, _, _ = quoter.functions.quoteExactInputSingle(params).call()
            
            print(f"SushiSwap response: amount_out_wei={amount_out_wei}")
            
            return Decimal(amount_out_wei) / (Decimal(10) ** dec_out)

        except Exception as e:
            print(f"Błąd quote_exact_in Sushiswap: {e}")
            return None