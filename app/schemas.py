from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LinkCreate(BaseModel):
    url: HttpUrl
    custom_code: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{3,32}$")
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class LinkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None


class DayClicks(BaseModel):
    date: str
    clicks: int


class LinkStats(BaseModel):
    code: str
    original_url: str
    total_clicks: int
    clicks_by_day: list[DayClicks]
