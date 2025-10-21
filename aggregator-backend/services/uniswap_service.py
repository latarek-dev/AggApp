from decimal import Decimal
from typing import Tuple, Optional
from config import uniswap_abi, w3
from token_manager import TokenManager
from web3 import Web3
from pools_config import TOKENS
from .base_dex_service import BaseDexService
from .calculation_service import mid_price_from_univ3_sqrt

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

class UniswapService(BaseDexService):
    """Serwis pobierający ceny z Uniswap V3."""
    abi = uniswap_abi

    def get_dex_fee_percent(self, pool_address: str) -> Optional[Decimal]:
        """Zwraca fee z puli Uniswap V3 w formacie dziesiętnym (np. 0.003 dla 0.3%)."""
        try:
            pool_contract = w3.eth.contract(address=pool_address, abi=self.abi)
            fee_micro = pool_contract.functions.fee().call()
            return Decimal(fee_micro) / Decimal(1_000_000)
        except Exception as e:
            print(f"Błąd fee Uniswap {pool_address}: {e}")
            return None

    def get_mid_price(self, pool_address, token_from, token_to, token_decimals, token_addresses=None) -> Optional[Decimal]:
        """
        Pobiera mid-price z slot0 dla Uniswap V3.
        
        Args:
            pool_address: adres puli
            token_from: symbol tokenu wejściowego
            token_to: symbol tokenu wyjściowego
            token_decimals: (dec0, dec1) decimals tokenów
            token_addresses: (token0, token1) adresy z config (opcjonalne)
            
        Returns:
            Decimal: mid-price (token_to / token_from)
        """
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
            print(f"Błąd mid_price Uniswap: {e}")
            return None

    def quote_exact_in(self, pool_address, token_from, token_to, amount_in, token_decimals, token_addresses=None, pool_fee=None, pair=None) -> Optional[Decimal]:
        """
        Pobiera dokładny quote z Quoter V3 dla Uniswap.
        
        Args:
            pool_address: adres puli
            token_from: symbol tokenu wejściowego
            token_to: symbol tokenu wyjściowego
            amount_in: ilość tokenów wejściowych
            token_decimals: (dec0, dec1) decimals tokenów
            token_addresses: (token0, token1) adresy z config (opcjonalne)
            pool_fee: fee tier z config (opcjonalne, eliminuje blockchain call)
            pair: nazwa pary (opcjonalne, do fallback)
            
        Returns:
            Decimal: amount_out (już z fee)
        """
        try:
            pool   = w3.eth.contract(address=Web3.to_checksum_address(pool_address), abi=self.abi)
            quoter = w3.eth.contract(address=QUOTER_ADDRESS, abi=quoter_abi)
            
            if pool_fee:
                fee_tier = pool_fee
            else:
                fee_tier = pool.functions.fee().call()

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
            
            print(f"Quoter call: token_in={token_from} ({dec_in} dec), token_out={token_to} ({dec_out} dec), amount_in={amount_in_wei}")
            
            amount_out_wei = quoter.functions.quoteExactInputSingle(
                token_in_addr, token_out_addr, fee_tier, amount_in_wei, 0
            ).call()
            
            print(f"Quoter response: amount_out_wei={amount_out_wei}")
            
            return Decimal(amount_out_wei) / Decimal(10 ** dec_out)
        except Exception as e:
            print(f"Błąd quote_exact_in Uniswap: {e}")
            return None