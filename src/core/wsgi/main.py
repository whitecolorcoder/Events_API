from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

from src.database.db_connect import SessionLocal
from src.routers.api import router as api_router
from src.routers.health import router as health_router
from src.services.sync_service import SyncService

app = FastAPI()

app.include_router(api_router)
app.include_router(health_router)

scheduler = AsyncIOScheduler()


def daily_sync():
    db = SessionLocal()
    try:
        SyncService(db).sync()
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(daily_sync, CronTrigger(hour=0, minute=0))
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
