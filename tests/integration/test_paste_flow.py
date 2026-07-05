import re


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    return match.group(1)


def test_create_then_view_paste_round_trip_against_real_dynamodb(client):
    form_html = client.get("/").get_data(as_text=True)
    csrf_token = _extract_csrf_token(form_html)

    create_response = client.post(
        "/", data={"content": "integration test paste", "csrf_token": csrf_token}
    )
    assert create_response.status_code == 302

    view_response = client.get(create_response.headers["Location"])

    assert view_response.status_code == 200
    assert b"integration test paste" in view_response.data
    assert view_response.headers["Cache-Control"] == "public, max-age=31536000, immutable"


def test_view_unknown_paste_returns_404_against_real_dynamodb(client):
    response = client.get("/doesnotexist")

    assert response.status_code == 404
