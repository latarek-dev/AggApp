from decimal import Decimal
from typing import Tuple, List, Dict, Any, Optional
from config import erc20_abi, w3
from token_manager import TokenManager
from web3 import Web3
from pools_config import TOKENS, DEX_CONFIGS
import time

token_manager = TokenManager(TOKENS)

_gas_price_cache = {'value': None, 'timestamp': 0}

def get_cached_gas_price():
    """Gas price z cache lub blockchain."""
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

    def estimate_gas_for_swap(
        self,
        token_in_address: str,
        token_out_address: str,
        amount_in_wei: int,
        fee_tier: int,
        router_address: str,
        user_address: str = "0x0000000000000000000000000000000000000001"
    ) -> int:
        """
        Estymuje gas używając eth_estimateGas."""
        try:
            deadline = int(time.time()) + 1200
            
            swap_params = {
                'tokenIn': Web3.to_checksum_address(token_in_address),
                'tokenOut': Web3.to_checksum_address(token_out_address),
                'fee': fee_tier,
                'recipient': user_address,
                'deadline': deadline,
                'amountIn': amount_in_wei,
                'amountOutMinimum': 0,
                'sqrtPriceLimitX96': 0
            }
            
            router_abi = self._get_router_abi()
            router_contract = w3.eth.contract(address=Web3.to_checksum_address(router_address), abi=router_abi)
            
            tx_data = router_contract.encode_abi('exactInputSingle', args=[swap_params])
            
            weth_address = TOKENS['ETH']['address'].lower()
            tx_value = amount_in_wei if token_in_address.lower() == weth_address else 0
            
            gas_estimate = w3.eth.estimate_gas({
                'from': user_address,
                'to': Web3.to_checksum_address(router_address),
                'data': tx_data,
                'value': tx_value
            })
            
            gas_with_buffer = int(gas_estimate * 1.05)
            
            print(f"Gas estimate dla {self.__class__.__name__}: {gas_estimate} (+5% = {gas_with_buffer})")
            return gas_with_buffer
            
        except Exception as e:
            print(f"Błąd estymacji gas dla {self.__class__.__name__}: {e}")
            return 150_000
    
    def _get_router_abi(self) -> list:
        """Zwraca ABI routera."""
        return [
            {
                "inputs": [
                    {
                        "components": [
                            {"internalType": "address", "name": "tokenIn", "type": "address"},
                            {"internalType": "address", "name": "tokenOut", "type": "address"},
                            {"internalType": "uint24", "name": "fee", "type": "uint24"},
                            {"internalType": "address", "name": "recipient", "type": "address"},
                            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                            {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                        ],
                        "internalType": "struct ISwapRouter.ExactInputSingleParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "exactInputSingle",
                "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]

    def get_gas_cost_usd(
        self,
        token_in_address: str,
        token_out_address: str,
        amount_in_wei: int,
        fee_tier: int,
        router_address: str,
        eth_price: Decimal
    ) -> Optional[Decimal]:
        """Oblicza koszt gazu w USD używając eth_estimateGas."""
        try:
            gas_estimate = self.estimate_gas_for_swap(
                token_in_address=token_in_address,
                token_out_address=token_out_address,
                amount_in_wei=amount_in_wei,
                fee_tier=fee_tier,
                router_address=router_address
            )
            
            gas_price_wei = get_cached_gas_price()
            gas_price_eth = Web3.from_wei(gas_price_wei, 'ether')
            
            gas_cost_eth = Decimal(gas_price_eth) * Decimal(gas_estimate)
            gas_cost_usd = gas_cost_eth * eth_price
            
            print(f"Gas cost: {gas_estimate} gas × {gas_price_wei} wei = ${gas_cost_usd:.5f}")
            return gas_cost_usd
            
        except Exception as e:
            print(f"Błąd obliczania gas cost dla {self.__class__.__name__}: {e}")
            return None

    def get_transaction_cost(
        self,
        pool_address: str,
        token_from_address: str,
        token_to_address: str,
        amount_in_wei: int,
        fee_tier: int,
        router_address: str,
        liquidity: float,
        eth_price: Decimal
    ) -> Tuple[Optional[Decimal], Optional[Decimal]]:
        """Zwraca (dex_fee, gas_cost_usd)."""
        try:
            dex_fee = self.get_dex_fee_percent(pool_address)
            
            if dex_fee is None:
                return None, None
            
            gas_cost = self.get_gas_cost_usd(
                token_in_address=token_from_address,
                token_out_address=token_to_address,
                amount_in_wei=amount_in_wei,
                fee_tier=fee_tier,
                router_address=router_address,
                eth_price=eth_price
            )

            if gas_cost is None:
                return None, None

            return dex_fee, gas_cost

        except Exception as e:
            print(f"Błąd przy obliczaniu kosztów transakcji {self.__class__.__name__}: {e}")
            return None, None
