from web3 import Web3
import json
import redis.asyncio as redis
from decimal import getcontext

# Ustawienie precyzji dla obliczeń dziesiętnych
getcontext().prec = 50

# Połączenie z siecią Arbitrum
RPC_URL = 'https://arb1.arbitrum.io/rpc'
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():
    print("Połączono z siecią Arbitrum!")
else:
    print("Nie udało się połączyć z siecią!")

# Wczytaj ABI Uniswap V3 i SushiSwap (zakładając, że masz odpowiednie ABI)
with open('uniswap_abi.json') as f:
    uniswap_abi = json.load(f)

with open('sushiswap_abi.json') as f:
    sushiswap_abi = json.load(f)

with open('camelot_abi.json') as f:
    camelot_abi = json.load(f)

# Konfiguracja Redis
REDIS_URL = "redis://localhost:6379"


async def get_redis():
    return redis.Redis(host="localhost", port=6379, decode_responses=True)