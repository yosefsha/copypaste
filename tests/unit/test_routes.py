import re

from copypaste import db


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return match.group(1)


def test_get_create_form_renders_textarea(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<textarea" in response.data


def test_post_create_redirects_to_view_url(client):
    form_html = client.get("/").get_data(as_text=True)
    csrf_token = _extract_csrf_token(form_html)

    response = client.post("/", data={"content": "hello world", "csrf_token": csrf_token})

    assert response.status_code == 302
    assert re.match(r"^/[0-9A-Za-z]{7}$", response.headers["Location"])


def test_post_create_without_csrf_token_is_rejected(client):
    response = client.post("/", data={"content": "hello world"})

    assert response.status_code == 400


def test_post_create_rejects_oversized_content(client):
    form_html = client.get("/").get_data(as_text=True)
    csrf_token = _extract_csrf_token(form_html)
    oversized = "x" * (db.MAX_PASTE_SIZE_BYTES + 1)

    response = client.post("/", data={"content": oversized, "csrf_token": csrf_token})

    assert response.status_code == 400


def test_view_existing_paste_renders_content_with_immutable_cache_header(client, dynamodb_table):
    paste_id = db.put_paste(dynamodb_table, "hello world")

    response = client.get(f"/{paste_id}")

    assert response.status_code == 200
    assert b"hello world" in response.data
    assert response.headers["Cache-Control"] == "public, max-age=31536000, immutable"


def test_post_create_with_title_renders_title_on_view_page(client):
    form_html = client.get("/").get_data(as_text=True)
    csrf_token = _extract_csrf_token(form_html)

    create_response = client.post(
        "/", data={"content": "hello world", "title": "My Paste", "csrf_token": csrf_token}
    )
    view_response = client.get(create_response.headers["Location"])

    assert b"My Paste" in view_response.data


def test_view_unknown_paste_returns_404(client):
    response = client.get("/nonexist")

    assert response.status_code == 404


def test_post_create_with_expiration_still_creates_a_viewable_paste(client):
    form_html = client.get("/").get_data(as_text=True)
    csrf_token = _extract_csrf_token(form_html)

    create_response = client.post(
        "/", data={"content": "hello world", "expiration": "3600", "csrf_token": csrf_token}
    )
    view_response = client.get(create_response.headers["Location"])

    assert view_response.status_code == 200
    assert b"hello world" in view_response.data


def test_view_expired_paste_returns_404(client, dynamodb_table):
    paste_id = db.put_paste(dynamodb_table, "hello world", expires_in_seconds=-1)

    response = client.get(f"/{paste_id}")

    assert response.status_code == 404
