from web3 import Web3
import json
import os
from decimal import getcontext

# Ustawienie precyzji dla obliczeń dziesiętnych
getcontext().prec = 50

RPC_URL = os.getenv("RPC_URL", "https://arb1.arbitrum.io/rpc")
REDIS_URL = os.getenv("REDIS_URL", "redis://:redispw@redis:6379/0")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if w3.is_connected():
    print("Połączono z siecią Arbitrum!")
else:
    print("Nie udało się połączyć z siecią!")

with open('uniswap_abi.json') as f:
    uniswap_abi = json.load(f)

with open('sushiswap_abi.json') as f:
    sushiswap_abi = json.load(f)

with open('camelot_abi.json') as f:
    camelot_abi = json.load(f)

with open('erc20_abi.json') as f:
    erc20_abi = json.load(f)