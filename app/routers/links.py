import secrets
import string
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Click, Link, User, utcnow
from app.schemas import LinkCreate, LinkOut, LinkStats

router = APIRouter(prefix="/links", tags=["links"])
ALPHABET = string.ascii_letters + string.digits


def generate_unique_code(db: Session, length: int = 6) -> str:
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(length))
        if not db.scalar(select(Link).where(Link.code == code)):
            return code


def get_owned_link(db: Session, code: str, user: User) -> Link:
    link = db.scalar(select(Link).where(Link.code == code))
    if not link or link.owner_id != user.id:
        raise HTTPException(404, "Link não encontrado")
    return link


@router.post("", response_model=LinkOut, status_code=201)
def create_link(
    data: LinkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.custom_code:
        if db.scalar(select(Link).where(Link.code == data.custom_code)):
            raise HTTPException(409, "Código já em uso")
        code = data.custom_code
    else:
        code = generate_unique_code(db)

    expires_at = utcnow() + timedelta(days=data.expires_in_days) if data.expires_in_days else None
    link = Link(code=code, original_url=str(data.url), expires_at=expires_at, owner_id=user.id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.get("", response_model=list[LinkOut])
def list_links(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(
        select(Link).where(Link.owner_id == user.id).order_by(Link.created_at.desc())
    ).all()


@router.get("/{code}/stats", response_model=LinkStats)
def link_stats(code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    link = get_owned_link(db, code, user)
    total = db.scalar(select(func.count(Click.id)).where(Click.link_id == link.id))
    day = func.date(Click.clicked_at)
    rows = db.execute(
        select(day, func.count(Click.id))
        .where(Click.link_id == link.id)
        .group_by(day)
        .order_by(day)
    ).all()
    return LinkStats(
        code=link.code,
        original_url=link.original_url,
        total_clicks=total or 0,
        clicks_by_day=[{"date": str(d), "clicks": c} for d, c in rows],
    )


@router.delete("/{code}", status_code=204)
def delete_link(code: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    link = get_owned_link(db, code, user)
    db.delete(link)
    db.commit()
    return Response(status_code=204)
