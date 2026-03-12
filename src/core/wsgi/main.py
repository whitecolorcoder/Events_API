from fastapi import FastAPI
from src.routers.api import router as api_router
from src.routers.health import router as health_router

app = FastAPI()

app.include_router(api_router)
app.include_router(health_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

