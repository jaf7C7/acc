import os
import pytest  # noqa: F401
import superpy


def test_returns_1_if_no_args():
    assert superpy.main() == 1


def test_returns_0_if_args():
    assert superpy.main(["frobble"]) == 0


def test_date_without_args_prints_the_default_date(capsys):
    superpy.main(["date"])
    out, err = capsys.readouterr()
    assert out == "1970-01-01\n"


def test_can_set_and_get_the_date(capsys):
    superpy.main(["date", "2020-02-02"])
    superpy.main(["date"])
    out, err = capsys.readouterr()
    assert out == "2020-02-02\n"
    os.unlink("superpy_date")


@pytest.mark.parametrize(
    "days, expected",
    [("", "1970-01-02\n"), ("30", "1970-01-31\n"), ("366", "1971-01-02\n")],
)
def test_can_advance_date_by_days(capsys, days, expected):
    try:
        superpy.main(["date", "--advance", days])
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == expected
    finally:
        os.unlink("superpy_date")
