from fastapi import FastAPI
from src.routers.health import router as health_router
from src.routers.sync import router as sync_router
from src.routers.events import router as events_router


app = FastAPI()

app.include_router(sync_router)
app.include_router(health_router)
app.include_router(events_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0", port=8000)

