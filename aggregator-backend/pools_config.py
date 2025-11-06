from typing import Dict, Any, List, Optional

TOKENS = {
    "USDC": {
        "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "decimals": 6,
        "coingecko_id": "usd-coin",
        "symbol": "USDC", 
        "name": "USD Coin"
    },
    "USDT": {
        "address": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "decimals": 6,
        "coingecko_id": "tether",
        "symbol": "USDT",
        "name": "Tether USD"
    },
    "DAI": {
        "address": "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
        "decimals": 18,
        "coingecko_id": "dai",
        "symbol": "DAI",
        "name": "Dai Stablecoin"
    },
    "ETH": {
        "address": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "decimals": 18,
        "coingecko_id": "ethereum",
        "symbol": "ETH",
        "name": "Ethereum"
    },
    "WBTC": {
        "address": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
        "decimals": 8,
        "coingecko_id": "wrapped-bitcoin",
        "symbol": "WBTC",
        "name": "Wrapped Bitcoin"
    }
}

DEX_CONFIGS = {
    "Uniswap": {
        "chain_id": 42161,
        "name": "Uniswap V3",
        "version": "V3",
        "contracts": {
            "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"
        },
        "fee_tiers": [100, 500, 3000, 10000],
        "pools": {
            "USDC/ETH": {"address": "0xC6962004f452bE9203591991D15f6b388e09E8D0", "fee": 500},
            "USDT/ETH": {"address": "0x641C00A822e8b671738d32a431a4Fb6074E5c79d", "fee": 500},
            "DAI/ETH": {"address": "0xA961F0473dA4864C5eD28e00FcC53a3AAb056c1b", "fee": 3000},
            "USDC/DAI": {"address": "0x7CF803e8d82A50504180f417B8bC7a493C0a0503", "fee": 100},
            "USDT/DAI": {"address": "0x7f580f8A02b759C350E6b8340e7c2d4b8162b6a9", "fee": 100},
            "ETH/WBTC": {"address": "0x2f5e87C9312fa29aed5c179E456625D79015299c", "fee": 500},
            "USDC/USDT": {"address": "0xbE3aD6a5669Dc0B8b12FeBC03608860C31E2eef6", "fee": 100},
            "USDT/WBTC": {"address": "0x5969EFddE3cF5C0D9a88aE51E47d721096A97203", "fee": 500}
        }
    },
    
    "SushiSwap": {
        "chain_id": 42161,
        "name": "SushiSwap V3",
        "version": "V3",
        "contracts": {
            "router": "0x8A21F6768C1f8075791D08546Dadf6daA0bE820c",
            "quoter": "0x0524E833cCD057e4d7A296e3aaAb9f7675964Ce1"
        },
        "fee_tiers": [100, 500, 3000, 10000],
        "pools": {
            "USDC/ETH": {"address": "0xf3Eb87C1F6020982173C908E7eB31aA66c1f0296", "fee": 500},
            "USDT/ETH": {"address": "0x96aDA81328abCe21939A51D971A63077e16db26E", "fee": 500},
            "DAI/ETH": {"address": "0x3370EA4a1640C657bDD94D71325541bA927f5Aef", "fee": 3000},
            "USDC/DAI": {"address": "0x5DcF1Aa6B3422D8A59dc0e00904E02A1c1ea5a58", "fee": 100},
            "USDT/DAI": {"address": "0xCc2B91d28d754DFF160d0924e16e6d213cBD24F8", "fee": 3000},
            "ETH/WBTC": {"address": "0x6F10667F314498649eb2f80da244e8c6E9f031d5", "fee": 3000},
            "USDC/USDT": {"address": "0xD1E1Ac29B31B35646EaBD77163E212b76fE3b6A2", "fee": 100},
            "USDC/WBTC": {"address": "0x699f628A8A1DE0f28cf9181C1F8ED848eBB0BBdF", "fee": 500},
            "USDT/WBTC": {"address": "0x0EE21120c8C527ECa08Cb5336E86Abf380994b4e", "fee": 3000}
        }
    },
    
    "Camelot": {
        "chain_id": 42161,
        "name": "Camelot V3",
        "version": "V3",
        "contracts": {
            "router": "0x1F721E2E82F6676FCE4eA07A5958cF098D339e18",
            "quoter": "0x0Fc73040b26E9bC8514fA028D998E73A254Fa76E"
        },
        "fee_tiers": [100, 500, 3000, 10000],
        "pools": {
            "USDC/ETH": {"address": "0xB1026b8e7276e7AC75410F1fcbbe21796e8f7526", "fee": None},
            "USDT/ETH": {"address": "0x7CcCBA38E2D959fe135e79AEBB57CCb27B128358", "fee": None},
            "USDC/DAI": {"address": "0x45FaE8D0D2acE73544baab452f9020925AfCCC75", "fee": None},
            "ETH/WBTC": {"address": "0xd845f7D4f4DeB9Ff5bCf09D140Ef13718F6f6C71", "fee": None},
            "USDC/USDT": {"address": "0xa17aFCAb059F3C6751F5B64347b5a503C3291868", "fee": None},
            "USDC/WBTC": {"address": "0x02bE4f98FC9Ee4F612a139D84494CBf6c6c7F97f", "fee": None},
        }
    }
}

def get_token_config(symbol: str) -> Dict[str, Any]:
    """Pobiera konfigurację tokenu po symbolu."""
    return TOKENS.get(symbol.upper())

def get_dex_config(dex_name: str) -> Dict[str, Any]:
    """Pobiera konfigurację DEX-a po nazwie."""
    return DEX_CONFIGS.get(dex_name)

def get_pool_config(dex_name: str, pair: str) -> Dict[str, Any]:
    """Pobiera konfigurację puli dla konkretnego DEX-a i pary."""
    dex_config = get_dex_config(dex_name)
    if not dex_config:
        return None
    return dex_config.get("pools", {}).get(pair)

def get_contract_address(dex_name: str, contract_type: str) -> str:
    """Pobiera adres kontraktu dla konkretnego DEX-a."""
    dex_config = get_dex_config(dex_name)
    if not dex_config:
        return None
    return dex_config.get("contracts", {}).get(contract_type)

def get_all_supported_tokens() -> List[str]:
    """Zwraca listę wszystkich obsługiwanych tokenów."""
    return list(TOKENS.keys())

def get_all_dex_names() -> List[str]:
    """Zwraca listę wszystkich obsługiwanych DEX-ów."""
    return list(DEX_CONFIGS.keys())

def get_pool_fee(dex_name: str, pair: str) -> Optional[int]:
    """Fee tier z config (np. 500 dla 0.05%)."""
    pool_config = get_pool_config(dex_name, pair)
    if pool_config:
        return pool_config.get("fee")
    return None

UNISWAP_POOLS = DEX_CONFIGS["Uniswap"]["pools"]
SUSHISWAP_POOLS = DEX_CONFIGS["SushiSwap"]["pools"]
CAMELOT_POOLS  = DEX_CONFIGS["Camelot"]["pools"]