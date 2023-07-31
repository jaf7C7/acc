import os
import pytest  # noqa: F401
import superpy


@pytest.mark.active
def test_returns_1_if_no_args():
    assert superpy.main() == 1


@pytest.mark.active
def test_returns_0_if_known_args():
    assert superpy.main(["date"]) == 0


@pytest.mark.active
def test_date_without_args_prints_the_default_date(capsys):
    superpy.main(["date"])
    out, err = capsys.readouterr()
    assert out == "1970-01-01\n"


@pytest.mark.active
def test_can_set_and_get_the_date(capsys):
    try:
        superpy.main(["date", "2020-02-02"])
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == "2020-02-02\n"
    finally:
        os.unlink(".superpy.conf")


@pytest.mark.active
@pytest.mark.parametrize(
    "days, expected",
    [("", "1970-01-02\n"), ("30", "1970-01-31\n"), ("366", "1971-01-02\n")],
)
def test_can_advance_date_by_days(capsys, days, expected):
    try:
        superpy.main(f"date --advance {days}".split())
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == expected
    finally:
        os.unlink(".superpy.conf")


@pytest.mark.active
def test_ledger_without_args_prints_the_default_ledger_path(capsys):
    superpy.main(["ledger"])
    out, err = capsys.readouterr()
    assert out == "superpy_ledger.csv\n"


def test_can_set_and_get_the_ledger_path(capsys):
    try:
        superpy.main(["ledger", "/tmp/foo"])
        superpy.main(["ledger"])
        out, err = capsys.readouterr()
        assert out == "/tmp/foo\n"
    finally:
        os.unlink(".superpy.conf")
