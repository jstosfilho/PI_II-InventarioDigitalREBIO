from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    postgis = db.execute(text("SELECT PostGIS_Version()")).scalar()
    return {"status": "ok", "postgis": postgis}
