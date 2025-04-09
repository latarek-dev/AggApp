
# Słownik par tokenów z pulami i decymalnymi
UNISWAP_POOLS = {
    "USDC/ETH": {"address": "0xC6962004f452bE9203591991D15f6b388e09E8D0", "decimals": (6, 18)},
    "USDT/ETH": {"address": "0x641C00A822e8b671738d32a431a4Fb6074E5c79d", "decimals": (6, 18)},
    "DAI/ETH":  {"address": "0xA961F0473dA4864C5eD28e00FcC53a3AAb056c1b", "decimals": (18, 18)},
    "USDC/DAI": {"address": "0x7CF803e8d82A50504180f417B8bC7a493C0a0503", "decimals": (18, 6)},
    "USDT/DAI": {"address": "0x7f580f8A02b759C350E6b8340e7c2d4b8162b6a9", "decimals": (6, 18)},
    "ETH/WBTC": {"address": "0x2f5e87C9312fa29aed5c179E456625D79015299c", "decimals": (18, 8)},
}

SUSHISWAP_POOLS = {
    "USDC/ETH": {"address": "0xf3Eb87C1F6020982173C908E7eB31aA66c1f0296", "decimals": (6, 18)},
    "USDT/ETH": {"address": "0x96aDA81328abCe21939A51D971A63077e16db26E", "decimals": (6, 18)},
    "DAI/ETH":  {"address": "0x3370EA4a1640C657bDD94D71325541bA927f5Aef", "decimals": (18, 18)},
    "USDC/DAI": {"address": "0x5DcF1Aa6B3422D8A59dc0e00904E02A1c1ea5a58", "decimals": (18, 6)},
    "USDT/DAI": {"address": "0xCc2B91d28d754DFF160d0924e16e6d213cBD24F8", "decimals": (6, 18)},
    "ETH/WBTC": {"address": "0x6F10667F314498649eb2f80da244e8c6E9f031d5", "decimals": (18, 8)},
}

CAMELOT_POOLS = {
    "USDC/ETH": {"address": "0xB1026b8e7276e7AC75410F1fcbbe21796e8f7526", "decimals": (6, 18)},  # Podmień na prawdziwe adresy
    "USDT/ETH": {"address": "0x7CcCBA38E2D959fe135e79AEBB57CCb27B128358", "decimals": (6, 18)},
}

# Słownik tokenów i ich identyfikatorów na CoinGecko
TOKEN_IDS = {
    "USDC": "usd-coin",          # USDC na CoinGecko to 'usd-coin'
    "USDT": "tether",            # USDT na CoinGecko to 'tether'
    "DAI":  "dai",               # DAI na CoinGecko to 'dai'
    "ETH":  "ethereum",          # ETH na CoinGecko to 'ethereum'
    "WBTC": "wrapped-bitcoin"    # WBTC na CoinGecko to 'wrapped-bitcoin'
}