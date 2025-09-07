import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi import Request
from routes import exchange_router
from services.redis_service import redis_service

async def lifespan_handler(app: FastAPI):
    try:
        success = await redis_service.connect()
        if success:
            print(f"Połączono z Redis!")
        else:
            print(f"[Startup] Nie udało się połączyć z Redis")
    except Exception as e:
        print(f"[Startup] Błąd podczas łączenia z Redis: {e}")

    yield
    # Zamykanie połączenia z Redis
    await redis_service.close()
    print("Zamknięto połączenie z Redis")


app = FastAPI(
    lifespan=lifespan_handler
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(exchange_router)

@app.get("/")
async def root():
    return {"message": "API działa poprawnie"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)