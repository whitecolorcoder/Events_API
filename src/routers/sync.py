from fastapi import APIRouter
from src.routers.deps import SessionDep
from src.services.sync_service import SyncService

router = APIRouter(prefix="/sync")


@router.post("")
def sync(db: SessionDep):
    SyncService(db).sync()
    return {"status": "ok"}