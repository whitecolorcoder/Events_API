from fastapi import APIRouter

from src.routers.deps import SessionDep
from src.services.sync_service import SyncService

router = APIRouter(prefix="/api")


@router.post("/sync/trigger")
def trigger_sync(db: SessionDep):
    SyncService(db).sync()
    return {"status": "ok"}
