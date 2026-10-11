from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Click, Link, utcnow

router = APIRouter(tags=["redirect"])


@router.get("/{code}")
def redirect(code: str, request: Request, db: Session = Depends(get_db)):
    link = db.scalar(select(Link).where(Link.code == code))
    if not link:
        raise HTTPException(404, "Link não encontrado")
    if link.expires_at and link.expires_at < utcnow():
        raise HTTPException(410, "Link expirado")

    db.add(
        Click(
            link_id=link.id,
            user_agent=request.headers.get("user-agent"),
            referer=request.headers.get("referer"),
        )
    )
    db.commit()
    return RedirectResponse(link.original_url, status_code=307)
