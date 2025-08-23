import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi import Request
from routes import exchange_router
import redis.asyncio as redis
from config import REDIS_URL

async def lifespan_handler(app: FastAPI):
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    try:
        await redis_client.ping()
        print(f"Połączono z Redis! ({REDIS_URL})")
    except Exception as e:
        print(f"[Startup] Nie udało się połączyć z Redis ({REDIS_URL}): {e}")

    yield
    await redis_client.close()
    print("Zamknięto połączenie z Redis")


app = FastAPI(
    lifespan=lifespan_handler
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(exchange_router)

@app.get("/")
async def root():
    return {"message": "API działa poprawnie"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)