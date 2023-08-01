import os
import pytest
import superpy


@pytest.mark.parametrize(
    "param, expected",
    [
        (None, dict(date="2000-01-01", ledger="/tmp/bar")),
        ("date", "2000-01-01"),
        ("ledger", "/tmp/bar"),
    ],
)
def test_get_config(param, expected):
    try:
        with open(".superpy.conf", "w") as c:
            c.write("\n".join(["2000-01-01", "/tmp/bar"]))
        assert superpy.get_config(param) == expected
    finally:
        os.unlink(".superpy.conf")


def test_set_config():
    try:
        superpy.set_config("date", "1664-08-17")
        superpy.set_config("ledger", "/tmp/frobble")
        with open(".superpy.conf", "r") as c:
            assert c.read().split() == ["1664-08-17", "/tmp/frobble"]
    finally:
        os.unlink(".superpy.conf")
