import pytest
from moto import mock_aws

from copypaste import db


@pytest.fixture
def table():
    with mock_aws():
        resource = db.get_resource()
        yield db.create_table(resource, table_name="pastes-test")


def test_put_and_get_paste_round_trip(table):
    paste_id = db.put_paste(table, "hello world")

    paste = db.get_paste(table, paste_id)
    assert paste.content == "hello world"
    assert paste.title is None


def test_put_and_get_paste_with_title(table):
    paste_id = db.put_paste(table, "hello world", title="My Paste")

    paste = db.get_paste(table, paste_id)
    assert paste.content == "hello world"
    assert paste.title == "My Paste"


def test_get_paste_returns_none_for_unknown_id(table):
    assert db.get_paste(table, "nonexist") is None


def test_put_paste_retries_on_id_collision(table, monkeypatch):
    ids = iter(["abcdef1", "abcdef1", "abcdef2"])
    monkeypatch.setattr(db, "generate_id", lambda: next(ids))

    first_id = db.put_paste(table, "first")
    second_id = db.put_paste(table, "second")

    assert first_id == "abcdef1"
    assert second_id == "abcdef2"


def test_put_paste_rejects_oversized_content(table):
    oversized = "x" * (db.MAX_PASTE_SIZE_BYTES + 1)

    with pytest.raises(db.PasteTooLargeError):
        db.put_paste(table, oversized)


def test_put_and_get_paste_with_no_expiration(table):
    paste_id = db.put_paste(table, "hello world")

    assert db.get_paste(table, paste_id).content == "hello world"


def test_get_paste_returns_none_for_expired_paste(table):
    paste_id = db.put_paste(table, "hello world", expires_in_seconds=-1)

    assert db.get_paste(table, paste_id) is None


def test_get_paste_returns_paste_that_has_not_expired_yet(table):
    paste_id = db.put_paste(table, "hello world", expires_in_seconds=3600)

    assert db.get_paste(table, paste_id).content == "hello world"


def test_put_and_get_paste_with_language(table):
    paste_id = db.put_paste(table, "print('hi')", language="python")

    paste = db.get_paste(table, paste_id)
    assert paste.content == "print('hi')"
    assert paste.language == "python"


def test_put_and_get_paste_without_language(table):
    paste_id = db.put_paste(table, "hello world")

    assert db.get_paste(table, paste_id).language is None
