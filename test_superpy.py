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


class TestCli:
    def test_date_without_args_prints_the_default_date(self, capsys, application):
        superpy.cli(["date"])
        out, err = capsys.readouterr()
        assert out == "1970-01-01\n"

    def test_can_set_and_get_the_date(self, capsys, application):
        superpy.cli(["date", "2020-02-02"])
        superpy.cli(["date"])
        out, err = capsys.readouterr()
        assert out == "2020-02-02\n"

    def test_fails_if_non_iso_format_date(self, application):
        assert superpy.cli(["date", "01/01/1970"]) == 1

    @pytest.mark.parametrize(
        "days, expected",
        [("", "1970-01-02\n"), ("30", "1970-01-31\n"), ("366", "1971-01-02\n")],
    )
    def test_can_advance_date_by_days(self, capsys, days, expected, application):
        superpy.cli(f"date --advance {days}".split())
        superpy.cli(["date"])
        out, err = capsys.readouterr()
        assert out == expected

    def test_fails_if_non_integer_days(self, application):
        assert superpy.cli(["date", "--advance", "0.5"]) == 1

    def test_ledger_without_args_prints_the_default_ledger(self, capsys, application):
        superpy.cli(["ledger"])
        out, err = capsys.readouterr()
        assert out == "superpy_ledger.csv\n"

    def test_date_and_ledger_can_be_set_independently(self, capsys, application):
        superpy.cli(["date", "1991-08-20"])
        superpy.cli(["ledger", "/tmp/foo"])
        superpy.cli(["date"])
        superpy.cli(["ledger"])
        out, err = capsys.readouterr()
        assert out.split() == ["1991-08-20", "/tmp/foo"]

    def test_can_set_and_get_the_ledger(self, capsys, application):
        superpy.cli(["ledger", "/tmp/foo"])
        superpy.cli(["ledger"])
        out, err = capsys.readouterr()
        assert out == "/tmp/foo\n"

    def test_can_record_and_recall_transactions(self, capsys, application):
        commands = [
            ["buy", "orange", "150"],
            ["buy", "apple", "85", "--units", "10"],
            ["buy", "a very large eastern halibut", "499", "--units", "5"],
            ["sell", "apple", "100", "--units", "5"],
            ["sell", "a very large eastern halibut", "250"],
        ]
        for command in commands:
            superpy.cli(command)
        with open("superpy_ledger.csv", "r") as ledger:
            assert list(csv.reader(ledger)) == [
                ["1970-01-01", "Purchase", "orange", "150", "1"],
                ["1970-01-01", "Purchase", "apple", "85", "10"],
                ["1970-01-01", "Purchase", "a very large eastern halibut", "499", "5"],
                ["1970-01-01", "Sale", "apple", "100", "5"],
                ["1970-01-01", "Sale", "a very large eastern halibut", "250", "1"],
            ]

    def test_report_fails_if_no_ledger_file(self, application):
        assert not os.path.exists("superpy_ledger.csv")
        assert superpy.cli(["report"]) == 1


class TestReadWriteLedger:
    def test_write(self, application):
        application.write_transaction_to_ledger(
            type="Purchase", product="Transonic Fremules", price=597, units=1
        )
        with open("superpy_ledger.csv", "r") as ledger:
            assert next(csv.reader(ledger)) == [
                "1970-01-01",
                "Purchase",
                "Transonic Fremules",
                "597",
                "1",
            ]


class TestParseArgs:
    @pytest.mark.active
    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["date"],
                argparse.Namespace(command="date", date=None, days=None),
            ),
            (
                ["date", "2020-02-02"],
                argparse.Namespace(
                    command="date",
                    date=datetime.date(2020, 2, 2),
                    days=None,
                ),
            ),
            (
                ["date", "--advance", "1"],
                argparse.Namespace(command="date", date=None, days=superpy.daydelta(1)),
            ),
            (
                ["date", "--advance"],
                argparse.Namespace(command="date", date=None, days=superpy.daydelta(1)),
            ),
            (["ledger"], argparse.Namespace(command="ledger", ledger=None)),
            (
                ["ledger", "/tmp/foo"],
                argparse.Namespace(command="ledger", ledger="/tmp/foo"),
            ),
            (
                ["buy", "orange", "15"],
                argparse.Namespace(command="buy", product="orange", price=15, units=1),
            ),
            (
                ["buy", "apple", "75", "--units", "42"],
                argparse.Namespace(command="buy", product="apple", price=75, units=42),
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


class TestReport:
    @pytest.fixture(autouse=True)
    def ledger_file(self):
        transactions = [
            ["1970-01-01", "Purchase", "frobule", "150", "1"],
            ["1970-01-01", "Purchase", "wobjock", "85", "10"],
            ["1970-01-01", "Purchase", "frobulator", "499", "5"],
            ["1970-01-01", "Sale", "wobjock", "400", "10"],
            ["1970-01-01", "Sale", "frobulator", "1050", "5"],
        ]
        with open("superpy_ledger.csv", "w") as ledger:
            writer = csv.writer(ledger)
            for transaction in transactions:
                writer.writerow(transaction)

    def test_default(self, capsys):
        superpy.cli(["report"])
        out, err = capsys.readouterr()
        assert (
            out
            == """\
DATE        TYPE      PRODUCT     PRICE   UNITS   TOTAL
1970-01-01  Purchase  frobule     150     1       -150
1970-01-01  Purchase  wobjock     85      10      -850
1970-01-01  Purchase  frobulator  499     5       -2495
1970-01-01  Sale      wobjock     400     10      +4000
1970-01-01  Sale      frobulator  1050    5       +5250
"""
        )
