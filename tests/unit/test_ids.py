import re

from copypaste.ids import generate_id

BASE62_ID_PATTERN = re.compile(r"^[0-9A-Za-z]{7}$")


def test_generate_id_is_seven_char_base62():
    assert BASE62_ID_PATTERN.match(generate_id())


def test_generate_id_is_random():
    ids = {generate_id() for _ in range(100)}

    assert len(ids) == 100
