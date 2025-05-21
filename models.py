from pydantic import BaseModel

class ExchangeRequest(BaseModel):
    token_from: str
    token_to: str
    amount: float

class FrontendTransactionOption(BaseModel):
    dex: str
    pair: str
    amount_from: float
    amount_to: float
    value_from_usd: float
    value_to_usd: float

class TransactionOptionRaw(BaseModel):
    dex: str
    pool: str
    amount_to: float
    slippage: float
    liquidity: float
    dex_fee: float
    gas_cost: float

class TransactionOption(BaseModel):
    dex: str
    pool: str
    price: float
    slippage: float
    liquidity: float
    dex_fee: float
    gas_cost: float
    amount_from: float
    amount_to: float
    value_from_usd: float
    value_to_usd: float