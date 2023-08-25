import os
import argparse
import datetime
import csv
import pytest
import acc
from decimal import Decimal


CONFIG_PATH = ".acc.conf"
LEDGER_PATH = "acc_ledger.csv"


@pytest.fixture
def application():
    return acc.Application()


@pytest.fixture(autouse=True)
def clean_up_test_files():
    yield
    for file in CONFIG_PATH, LEDGER_PATH:
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


class TestCli:
    def test_date_without_args_prints_the_default_date(self, capsys, application):
        acc.cli(["date"])
        out, err = capsys.readouterr()
        assert out == "1970-01-01\n"

    def test_can_set_and_get_the_date(self, capsys, application):
        acc.cli(["date", "2020-02-02"])
        acc.cli(["date"])
        out, err = capsys.readouterr()
        assert out == "2020-02-02\n"

    def test_fails_if_non_iso_format_date(self, application):
        assert acc.cli(["date", "01/01/1970"]) == 1

    @pytest.mark.parametrize(
        "days, expected",
        [("", "1970-01-02\n"), ("366", "1971-01-02\n")],
    )
    def test_can_advance_date_by_days(self, capsys, days, expected, application):
        acc.cli(f"date --advance {days}".split())
        acc.cli(["date"])
        out, err = capsys.readouterr()
        assert out == expected

    def test_fails_if_non_integer_days(self, application):
        assert acc.cli(["date", "--advance", "0.5"]) == 1

    def test_ledger_without_args_prints_the_default_ledger(self, capsys, application):
        acc.cli(["ledger"])
        out, err = capsys.readouterr()
        assert out == "acc_ledger.csv\n"

    def test_date_and_ledger_can_be_set_independently(self, capsys, application):
        acc.cli(["date", "1991-08-20"])
        acc.cli(["ledger", "/tmp/foo"])
        acc.cli(["date"])
        acc.cli(["ledger"])
        out, err = capsys.readouterr()
        assert out.split() == ["1991-08-20", "/tmp/foo"]

    def test_can_set_and_get_the_ledger(self, capsys, application):
        acc.cli(["ledger", "/tmp/foo"])
        acc.cli(["ledger"])
        out, err = capsys.readouterr()
        assert out == "/tmp/foo\n"

    def test_can_record_transactions(self, capsys, application):
        acc.cli(["credit", "850", "-d", "apple"])
        acc.cli(["debit", "500", "--description", "apple"])
        with open(LEDGER_PATH, "r", newline="") as ledger:
            assert list(csv.reader(ledger)) == [
                ["id", "date", "amount", "type", "description"],
                ["0", "1970-01-01", "850.00", "credit", "apple"],
                ["1", "1970-01-01", "500.00", "debit", "apple"],
            ]


class TestParseArgs:
    @pytest.mark.parametrize(
        "args, date, days",
        [
            (["date"], None, None),
            (["date", "2020-02-02"], datetime.date(2020, 2, 2), None),
            (["date", "--advance", "1"], None, acc.DayDelta(1)),
            (["date", "--advance"], None, acc.DayDelta(1)),
        ],
    )
    def test_date(self, args, date, days):
        assert acc.parse_args(args) == argparse.Namespace(
            command="date", date=date, days=days
        )

    @pytest.mark.parametrize(
        "args, ledger",
        [
            (["ledger"], None),
            (["ledger", "/tmp/foo"], acc.Ledger("/tmp/foo")),
        ],
    )
    def test_ledger(self, args, ledger):
        assert acc.parse_args(args) == argparse.Namespace(command="ledger", ledger=ledger)

    @pytest.mark.parametrize(
        "args, command, amount, description",
        [
            (
                ["credit", "15", "--description", "orange"],
                "credit",
                Decimal("15.00"),
                "orange",
            ),
            (["debit", "3150", "-d", "apple"], "debit", Decimal("3150.00"), "apple"),
        ],
    )
    def test_buy(self, args, command, amount, description):
        assert acc.parse_args(args) == argparse.Namespace(
            command=command, amount=amount, description=description
        )

    @pytest.mark.parametrize(
        "args, balance", [(["report"], False), (["report", "--balance"], True)]
    )
    def test_report(self, args, balance):
        assert acc.parse_args(args) == argparse.Namespace(
            command="report", balance=balance
        )

    @pytest.mark.parametrize(
        "args", [["date", "01/01/1970"], ["date", "--advance", "0.5"]]
    )
    def test_bad_arguments(self, args):
        with pytest.raises(argparse.ArgumentError):
            acc.parse_args(args)


class TestLedger:
    @pytest.fixture
    def mock_ledger(self):
        ledger = [
            ["id", "date", "amount", "type", "description"],
            ["0", "1970-01-01", "2495.00", "credit", "frobulator"],
            ["1", "1970-01-01", "5250.00", "debit", "frobulator"],
        ]
        with open(LEDGER_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            for transaction in ledger:
                writer.writerow(transaction)

    def test_write(self, application):
        ledger = acc.Ledger(LEDGER_PATH)
        ledger.append(
            id=len(ledger),
            date=datetime.date(1970, 1, 1).isoformat(),
            amount="{:.2f}".format(Decimal("597")),
            type="credit",
            description="Transonic Fremules",
        )
        with open(LEDGER_PATH, "r", newline="") as ledger:
            assert list(csv.reader(ledger)) == [
                ["id", "date", "amount", "type", "description"],
                ["0", "1970-01-01", "597.00", "credit", "Transonic Fremules"],
            ]

    def test_print(self, capsys, mock_ledger):
        acc.cli(["report"])
        out, err = capsys.readouterr()
        assert out == (
            "ID    DATE        AMOUNT    TYPE    DESCRIPTION\n"
            "0     1970-01-01  2495.00   credit  frobulator\n"
            "1     1970-01-01  5250.00   debit   frobulator\n"
        )

    def test_balance(self, capsys, mock_ledger):
        acc.cli(["report", "--balance"])
        out, err = capsys.readouterr()
        assert out == "2755.00\n"
