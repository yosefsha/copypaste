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

    assert db.get_paste(table, paste_id) == "hello world"


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
