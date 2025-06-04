import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi import Request
from routes import exchange_router
import redis.asyncio as redis  # Nowa wersja Redis
from config import REDIS_URL

# Funkcja lifespan do zarządzania połączeniem Redis
async def lifespan_handler(app: FastAPI):
    # Inicjalizacja Redis przy starcie aplikacji
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    print("Połączono z Redis!")
    
    yield  # Ten punkt oznacza "życie" aplikacji
    
    # Zamknięcie połączenia Redis przy zamykaniu aplikacji
    await redis_client.close()
    print("Zamknięto połączenie z Redis")

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    lifespan=lifespan_handler
)

# CORS – umożliwia połączenie z frontem React (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Podłączenie routera z endpointami wymiany
app.include_router(exchange_router)

@app.get("/")
async def root():
    return {"message": "API działa poprawnie"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)