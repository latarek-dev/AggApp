from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends
from models import ExchangeRequest
from pools_config import UNISWAP_POOLS, SUSHISWAP_POOLS, CAMELOT_POOLS, TOKEN_IDS
from services import CoinGeckoService, UniswapService, SushiswapService, CamelotService, RedisCacheService
from exchange_utils import process_dex_pools, process_prices

exchange_router = APIRouter()

# Dependency injection: Używamy CoinGeckoService oraz serwisów DEX
def get_services(redis_cache_service: RedisCacheService = Depends(),
                 coin_gecko_service: CoinGeckoService = Depends(), 
                 uniswap_service: UniswapService = Depends(),
                 sushiswap_service: SushiswapService = Depends(),
                 camelot_service: CamelotService = Depends()):
    return redis_cache_service, coin_gecko_service, uniswap_service, sushiswap_service, camelot_service

@exchange_router.post("/exchange")
async def exchange(request: ExchangeRequest,
                   services: tuple = Depends(get_services)):
    redis_cache_service, coin_gecko_service, uniswap_service, sushiswap_service, camelot_service = services
    print(f"Otrzymano żądanie z danymi: {request}")
    token_from = request.token_from.upper()
    token_to = request.token_to.upper()
    amount = request.amount
    print(f"Token_from: {token_from}, Token_to: {token_to}, Amount: {amount}")

    token_ids = [TOKEN_IDS[token] for token in [token_from, token_to] if token in TOKEN_IDS]
    print(f"Token IDs do pobrania z CoinGecko: {token_ids}")

    prices = await process_prices(coin_gecko_service, token_ids, redis_cache_service)

    all_options = []

    dexes = [
        ("Uniswap", UNISWAP_POOLS, uniswap_service, 'get_pair_price'),
        ("SushiSwap", SUSHISWAP_POOLS, sushiswap_service, 'get_pair_price'),
        ("Camelot", CAMELOT_POOLS, camelot_service, 'get_pair_price')
    ]

    for dex_name, pools, dex_service, price_method in dexes:
        dex_options = await process_dex_pools(dex_name, pools, dex_service, price_method, token_from, token_to, amount, redis_cache_service, prices)
        all_options.append(dex_options)

    all_options.sort(key=lambda x: x[2], reverse=True)
    print(f"Opcje wymiany po sortowaniu: {all_options}")

    if all_options:
        best_pool = all_options[0]
        print(f"Najlepsza opcja: {best_pool}")
        return {
            "best_option": {
                "dex": best_pool[0],
                "pair": best_pool[1],
                "amount_from": amount,
                "amount_to": float(best_pool[2]),
                "value_from_usd": best_pool[3],
                "value_to_usd": best_pool[4]
            },
            "options": [
                {
                    "dex": dex,
                    "pair": pair,
                    "amount_from": amount,
                    "amount_to": float(exchange_amount),
                    "value_from_usd": value_from_usd,
                    "value_to_usd": value_to_usd
                } for dex, pair, exchange_amount, value_from_usd, value_to_usd in all_options[1:]
            ]
        }
    else:
        print("Brak dostępnych opcji wymiany.")
        raise HTTPException(status_code=404, detail="No exchange options available.")
