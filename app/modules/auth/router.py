from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.auth import service

router = APIRouter(prefix="/auth", tags=["auth"])


def _google_login_redirect() -> RedirectResponse:
    return RedirectResponse(service.get_google_login_redirect_url())


@router.get("/google/login")
async def google_login_get():
    return _google_login_redirect()


@router.post("/google/login")
async def google_login_post():
    return _google_login_redirect()


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    target = await service.complete_google_oauth(db, code)
    return RedirectResponse(target)
