from decimal import Decimal
from fastapi import APIRouter, HTTPException, Depends
from models import ExchangeRequest, TransactionOption, TransactionOptionRaw, FrontendTransactionOption
from pools_config import UNISWAP_POOLS, SUSHISWAP_POOLS, CAMELOT_POOLS
from services import CoinGeckoService, UniswapService, SushiswapService, CamelotService, RedisCacheService
from exchange_utils import process_dex_pools, process_prices
from decision_engine import rank_options

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

    all_options = []

    dexes = [
        ("Uniswap", UNISWAP_POOLS, uniswap_service),
        ("SushiSwap", SUSHISWAP_POOLS, sushiswap_service),
        ("Camelot", CAMELOT_POOLS, camelot_service)
    ]

    for dex_name, pools, dex_service in dexes:
        dex_options = await process_dex_pools(dex_name, pools, dex_service, token_from, token_to, amount, redis_cache_service, coin_gecko_service)
        all_options.extend(dex_options)

    raw_options = [TransactionOptionRaw(
        dex=o.dex,
        pool=o.pool,
        amount_to=o.amount_to,
        slippage=o.slippage,
        liquidity=o.liquidity,
        tx_cost=o.tx_cost
    ) for o in all_options]

    # stwórz mapę do pełnych danych
    full_option_map = {
        (o.dex, o.pool): o
        for o in all_options
    }

    sorted_raw = rank_options(raw_options)

    print(f"Opcje wymiany po sortowaniu: {sorted_raw}")

    # mapujemy na FrontendTransactionOption
    frontend_sorted = []
    for raw in sorted_raw:
        full = full_option_map.get((raw.dex, raw.pool))
        if full:
            frontend_sorted.append(FrontendTransactionOption(
                dex=full.dex,
                pair=full.pool,
                amount_from=full.amount_from,
                amount_to=full.amount_to,
                value_from_usd=full.value_from_usd,
                value_to_usd=full.value_to_usd
            ))

    print(frontend_sorted)
    if frontend_sorted:
        return {
            "options": frontend_sorted
        }
    else:
        raise HTTPException(status_code=404, detail="No exchange options available.")

