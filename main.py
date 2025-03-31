import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
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
templates = Jinja2Templates(directory="templates")

# Podłączenie routera z endpointami wymiany
app.include_router(exchange_router)

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("exchange_app.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)