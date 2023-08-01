import os
import pytest
import superpy


def clean_up_test_files():
    for file in ".superpy.conf", "superpy_ledger.csv":
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


@pytest.mark.parametrize("args", [[""], ["frobble"]])
def test_returns_1_if_no_or_unknown_args(args):
    assert superpy.main(args) == 1


def test_returns_0_if_known_args():
    assert superpy.main(["date"]) == 0


def test_date_without_args_prints_the_default_date(capsys):
    superpy.main(["date"])
    out, err = capsys.readouterr()
    assert out == "1970-01-01\n"


def test_can_set_and_get_the_date(capsys):
    try:
        superpy.main(["date", "2020-02-02"])
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == "2020-02-02\n"
    finally:
        clean_up_test_files()


def test_fails_if_non_iso_format_date():
    try:
        assert superpy.main(["date", "01/01/1970"]) == 1
    finally:
        clean_up_test_files()


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
        clean_up_test_files()


def test_fails_if_non_integer_days():
    try:
        assert superpy.main(["date", "--advance", "0.5"]) == 1
    finally:
        clean_up_test_files()


def test_ledger_without_args_prints_the_default_ledger_path(capsys):
    superpy.main(["ledger"])
    out, err = capsys.readouterr()
    assert out == "superpy_ledger.csv\n"


def test_date_and_ledger_can_be_set_independently(capsys):
    try:
        superpy.main(["date", "1991-08-20"])
        superpy.main(["ledger", "/tmp/foo"])
        superpy.main(["date"])
        superpy.main(["ledger"])
        out, err = capsys.readouterr()
        assert out.split() == ["1991-08-20", "/tmp/foo"]
    finally:
        clean_up_test_files()


def test_can_set_and_get_the_ledger_path(capsys):
    try:
        superpy.main(["ledger", "/tmp/foo"])
        superpy.main(["ledger"])
        out, err = capsys.readouterr()
        assert out == "/tmp/foo\n"
    finally:
        clean_up_test_files()


def test_can_record_and_recall_a_purchase(capsys):
    try:
        transactions = [("orange", "1.50"), ("apple", "0.85"), ("halibut", "4.99")]
        expected = "\t".join(["DATE", "PRODUCT", "AMOUNT\n"])
        for product, price in transactions:
            superpy.main(["buy", product, price])
            expected += "\t".join(["1970-01-01", product, f"{price}\n"])
        superpy.main(["report"])
        out, err = capsys.readouterr()
        assert out == expected
    finally:
        clean_up_test_files()
