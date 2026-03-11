from fastapi import FastAPI
from src.routers.health import router as health_router
from src.routers.sync import router as sync_router
from src.routers.events import router as events_router
from src.database.base import Base
from src.database.db_connect import engine

app = FastAPI()



Base.metadata.create_all(bind=engine)

app.include_router(sync_router)
app.include_router(health_router)
app.include_router(events_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0", port=8000)

