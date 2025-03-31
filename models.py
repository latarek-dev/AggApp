from pydantic import BaseModel

class ExchangeRequest(BaseModel):
    token_from: str
    token_to: str
    amount: float

class TokenPair(BaseModel):
    token_a: str
    token_b: str
