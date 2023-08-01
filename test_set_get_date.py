import os
import superpy


def test_get_config():
    try:
        with open(".superpy.conf", "w") as c:
            c.write("\n".join(["2000-01-01", "/tmp/bar"]))
        assert superpy.get_config() == dict(date="2000-01-01", ledger="/tmp/bar")
    finally:
        os.unlink(".superpy.conf")
