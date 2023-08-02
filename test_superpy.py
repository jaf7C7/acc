import os
import argparse
import datetime
import pytest
import superpy


@pytest.fixture(autouse=True)
def clean_up_test_files():
    yield
    for file in ".superpy.conf", "superpy_ledger.csv":
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


class TestMain:
    def test_date_without_args_prints_the_default_date(self, capsys):
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == "1970-01-01\n"

    def test_can_set_and_get_the_date(self, capsys):
        superpy.main(["date", "2020-02-02"])
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == "2020-02-02\n"

    def test_fails_if_non_iso_format_date(self):
        assert superpy.main(["date", "01/01/1970"]) == 1

    @pytest.mark.parametrize(
        "days, expected",
        [("", "1970-01-02\n"), ("30", "1970-01-31\n"), ("366", "1971-01-02\n")],
    )
    def test_can_advance_date_by_days(self, capsys, days, expected):
        superpy.main(f"date --advance {days}".split())
        superpy.main(["date"])
        out, err = capsys.readouterr()
        assert out == expected

    def test_fails_if_non_integer_days(self):
        assert superpy.main(["date", "--advance", "0.5"]) == 1

    def test_ledger_without_args_prints_the_default_ledger_path(self, capsys):
        superpy.main(["ledger"])
        out, err = capsys.readouterr()
        assert out == "superpy_ledger.csv\n"

    def test_date_and_ledger_can_be_set_independently(self, capsys):
        superpy.main(["date", "1991-08-20"])
        superpy.main(["ledger", "/tmp/foo"])
        superpy.main(["date"])
        superpy.main(["ledger"])
        out, err = capsys.readouterr()
        assert out.split() == ["1991-08-20", "/tmp/foo"]

    def test_can_set_and_get_the_ledger_path(self, capsys):
        superpy.main(["ledger", "/tmp/foo"])
        superpy.main(["ledger"])
        out, err = capsys.readouterr()
        assert out == "/tmp/foo\n"

    def test_can_record_and_recall_a_purchase(self, capsys):
        transactions = [("orange", "1.50"), ("apple", "0.85"), ("halibut", "4.99")]
        expected = "\t".join(["DATE", "PRODUCT", "AMOUNT\n"])
        for product, price in transactions:
            superpy.main(["buy", product, price])
            expected += "\t".join(["1970-01-01", product, f"{price}\n"])
        superpy.main(["report"])
        out, err = capsys.readouterr()
        assert out == expected

    def test_report_fails_if_no_ledger_file(self):
        assert not os.path.exists("superpy_ledger.csv")
        assert superpy.main(["report"]) == 1


class TestSetGetConfig:
    @pytest.mark.parametrize(
        "param, expected",
        [
            (None, dict(date="2000-01-01", ledger="/tmp/bar")),
            ("date", "2000-01-01"),
            ("ledger", "/tmp/bar"),
        ],
    )
    def test_get_config(self, param, expected):
        with open(".superpy.conf", "w") as c:
            c.write("\n".join(["2000-01-01", "/tmp/bar"]))
        assert superpy.get_config(param) == expected

    def test_set_config(self):
        superpy.set_config("date", "1664-08-17")
        superpy.set_config("ledger", "/tmp/frobble")
        with open(".superpy.conf", "r") as c:
            assert c.read().split() == ["1664-08-17", "/tmp/frobble"]


class TestParseArgs:
    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["date"],
                argparse.Namespace(command="date", date=None, days_to_advance=None),
            ),
            (
                ["date", "2020-02-02"],
                argparse.Namespace(
                    command="date", date=datetime.date(2020, 2, 2), days_to_advance=None
                ),
            ),
            (
                ["date", "--advance", "1"],
                argparse.Namespace(command="date", date=None, days_to_advance=1),
            ),
            (
                ["date", "--advance"],
                argparse.Namespace(command="date", date=None, days_to_advance=1),
            ),
            (["ledger"], argparse.Namespace(command="ledger", ledger_path=None)),
            (
                ["ledger", "/tmp/foo"],
                argparse.Namespace(command="ledger", ledger_path="/tmp/foo"),
            ),
            (
                ["buy", "orange", "1.5"],
                argparse.Namespace(command="buy", product="orange", amount="1.5"),
            ),
            (["report"], argparse.Namespace(command="report")),
        ],
    )
    def test_returns_correct_namespace(self, args, expected):
        assert superpy.parse_args(args) == expected

    @pytest.mark.parametrize(
        "args", [["date", "01/01/1970"], ["date", "--advance", "0.5"]]
    )
    def test_bad_arguments(self, args):
        with pytest.raises(argparse.ArgumentError):
            superpy.parse_args(args)
