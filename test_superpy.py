import os
import argparse
import datetime
import csv
import pytest
import superpy


@pytest.fixture
def application():
    return superpy.Application()


@pytest.fixture(autouse=True)
def clean_up_test_files():
    yield
    for file in ".superpy.conf", "superpy_ledger.csv":
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


class TestMain:
    def test_date_without_args_prints_the_default_date(self, capsys, application):
        application.run(["date"])
        out, err = capsys.readouterr()
        assert out == "1970-01-01\n"

    def test_can_set_and_get_the_date(self, capsys, application):
        application.run(["date", "2020-02-02"])
        application.run(["date"])
        out, err = capsys.readouterr()
        assert out == "2020-02-02\n"

    def test_fails_if_non_iso_format_date(self, application):
        assert application.run(["date", "01/01/1970"]) == 1

    @pytest.mark.parametrize(
        "days, expected",
        [("", "1970-01-02\n"), ("30", "1970-01-31\n"), ("366", "1971-01-02\n")],
    )
    def test_can_advance_date_by_days(self, capsys, days, expected, application):
        application.run(f"date --advance {days}".split())
        application.run(["date"])
        out, err = capsys.readouterr()
        assert out == expected

    def test_fails_if_non_integer_days(self, application):
        assert application.run(["date", "--advance", "0.5"]) == 1

    def test_ledger_without_args_prints_the_default_ledger_path(
        self, capsys, application
    ):
        application.run(["ledger"])
        out, err = capsys.readouterr()
        assert out == "superpy_ledger.csv\n"

    def test_date_and_ledger_can_be_set_independently(self, capsys, application):
        application.run(["date", "1991-08-20"])
        application.run(["ledger", "/tmp/foo"])
        application.run(["date"])
        application.run(["ledger"])
        out, err = capsys.readouterr()
        assert out.split() == ["1991-08-20", "/tmp/foo"]

    def test_can_set_and_get_the_ledger_path(self, capsys, application):
        application.run(["ledger", "/tmp/foo"])
        application.run(["ledger"])
        out, err = capsys.readouterr()
        assert out == "/tmp/foo\n"

    def test_can_record_and_recall_a_purchase(self, capsys, application):
        transactions = [
            ("orange", "1.50"),
            ("apple", "0.85"),
            ("a very large eastern halibut", "4.99"),
        ]
        for product, price in transactions:
            application.run(["buy", product, price])
        application.run(["report"])
        out, err = capsys.readouterr()
        assert (
            out
            == """\
DATE        PRODUCT     AMOUNT
1970-01-01  orange      1.50
1970-01-01  apple       0.85
1970-01-01  a very large eastern halibut  4.99
"""
        )

    def test_report_fails_if_no_ledger_file(self, application):
        assert not os.path.exists("superpy_ledger.csv")
        assert application.run(["report"]) == 1


class TestReadWriteLedger:
    def test_write(self, application):
        application.write_transaction_to_ledger("Transonic Fremules", "5.97")
        with open("superpy_ledger.csv", "r") as ledger:
            assert next(csv.reader(ledger)) == [
                "1970-01-01",
                "Transonic Fremules",
                "5.97",
            ]


class TestParseArgs:
    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["date"],
                argparse.Namespace(command="date", new_date=None, days_to_advance=None),
            ),
            (
                ["date", "2020-02-02"],
                argparse.Namespace(
                    command="date",
                    new_date=datetime.date(2020, 2, 2),
                    days_to_advance=None,
                ),
            ),
            (
                ["date", "--advance", "1"],
                argparse.Namespace(
                    command="date", new_date=None, days_to_advance=superpy.daydelta(1)
                ),
            ),
            (
                ["date", "--advance"],
                argparse.Namespace(
                    command="date", new_date=None, days_to_advance=superpy.daydelta(1)
                ),
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
    def test_returns_correct_namespace(self, args, expected, application):
        assert application.parse_args(args) == expected

    @pytest.mark.parametrize(
        "args", [["date", "01/01/1970"], ["date", "--advance", "0.5"]]
    )
    def test_bad_arguments(self, args, application):
        with pytest.raises(argparse.ArgumentError):
            application.parse_args(args)
