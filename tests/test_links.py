from datetime import timedelta

from sqlalchemy import select

from app.models import Link, utcnow

URL = "https://example.com/pagina"


def create(client, headers, **extra):
    return client.post("/links", json={"url": URL, **extra}, headers=headers)


def test_requires_auth(client):
    assert client.post("/links", json={"url": URL}).status_code == 401


def test_create_and_redirect(client, auth_headers):
    code = create(client, auth_headers).json()["code"]
    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == URL


def test_custom_code_conflict(client, auth_headers):
    assert create(client, auth_headers, custom_code="meulink").status_code == 201
    assert create(client, auth_headers, custom_code="meulink").status_code == 409


def test_click_stats(client, auth_headers):
    code = create(client, auth_headers).json()["code"]
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)
    stats = client.get(f"/links/{code}/stats", headers=auth_headers).json()
    assert stats["total_clicks"] == 3
    assert stats["clicks_by_day"][0]["clicks"] == 3


def test_expired_link_returns_410(client, auth_headers, db):
    code = create(client, auth_headers, expires_in_days=1).json()["code"]
    link = db.scalar(select(Link).where(Link.code == code))
    link.expires_at = utcnow() - timedelta(days=1)
    db.commit()
    assert client.get(f"/{code}", follow_redirects=False).status_code == 410


def test_cannot_see_stats_of_other_user(client, auth_headers):
    code = create(client, auth_headers).json()["code"]
    other = {"email": "outro@exemplo.com", "password": "senha12345"}
    client.post("/auth/register", json=other)
    r = client.post("/auth/login", data={"username": other["email"], "password": other["password"]})
    other_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.get(f"/links/{code}/stats", headers=other_headers).status_code == 404
