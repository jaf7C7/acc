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

    def test_can_record_transactions(self, capsys, application):
        commands = [
            ["buy", "orange", "150"],
            ["buy", "apple", "85", "--units", "10"],
            ["buy", "a very large eastern halibut", "499", "--units", "5"],
            ["sell", "apple", "100", "--units", "5"],
            ["sell", "a very large eastern halibut", "250"],
        ]
        for command in commands:
            superpy.cli(command)
        with open("superpy_ledger.csv", "r", newline="") as ledger:
            assert list(csv.reader(ledger)) == [
                ["date", "product", "units", "debit", "credit", "balance"],
                ["1970-01-01", "orange", "1", "0", "150", "-150"],
                ["1970-01-01", "apple", "10", "0", "850", "-850"],
                [
                    "1970-01-01",
                    "a very large eastern halibut",
                    "5",
                    "0",
                    "2495",
                    "-2495",
                ],
                ["1970-01-01", "apple", "5", "500", "0", "500"],
                ["1970-01-01", "a very large eastern halibut", "1", "250", "0", "250"],
            ]


class TestParseArgs:
    @pytest.mark.parametrize(
        "args, date, days",
        [
            (["date"], None, None),
            (["date", "2020-02-02"], datetime.date(2020, 2, 2), None),
            (["date", "--advance", "1"], None, superpy.DayDelta(1)),
            (["date", "--advance"], None, superpy.DayDelta(1)),
        ],
    )
    def test_date(self, application, args, date, days):
        assert application.parse_args(args) == argparse.Namespace(
            command="date", date=date, days=days
        )

    @pytest.mark.parametrize(
        "args, ledger",
        [
            (["ledger"], None),
            (["ledger", "/tmp/foo"], superpy.Ledger("/tmp/foo")),
        ],
    )
    def test_ledger(self, application, args, ledger):
        assert application.parse_args(args) == argparse.Namespace(
            command="ledger", ledger=ledger
        )

    @pytest.mark.parametrize(
        "args, product, price, units",
        [
            (["buy", "orange", "15"], "orange", 15, 1),
            (["buy", "apple", "75", "--units", "42"], "apple", 75, 42),
        ],
    )
    def test_buy(self, application, args, product, price, units):
        assert application.parse_args(args) == argparse.Namespace(
            command="buy", product=product, price=price, units=units
        )

    @pytest.mark.parametrize(
        "args, balance", [(["report"], False), (["report", "--balance"], True)]
    )
    def test_report(self, application, args, balance):
        assert application.parse_args(args) == argparse.Namespace(
            command="report", balance=balance
        )

    @pytest.mark.parametrize(
        "args", [["date", "01/01/1970"], ["date", "--advance", "0.5"]]
    )
    def test_bad_arguments(self, args, application):
        with pytest.raises(argparse.ArgumentError):
            application.parse_args(args)


class TestLedger:
    @pytest.fixture
    def mock_ledger(self):
        ledger = [
            ["date", "product", "units", "debit", "credit", "balance"],
            ["1970-01-01", "frobule", "1", "0", "150", "-150"],
            ["1970-01-01", "wobjock", "10", "0", "850", "-850"],
            ["1970-01-01", "frobulator", "5", "0", "2495", "-2495"],
            ["1970-01-01", "wobjock", "10", "4000", "0", "4000"],
            ["1970-01-01", "frobulator", "5", "5250", "0", "5250"],
        ]
        with open("superpy_ledger.csv", "w", newline="") as f:
            writer = csv.writer(f)
            for transaction in ledger:
                writer.writerow(transaction)

    def test_write(self, application):
        ledger = superpy.Ledger("superpy_ledger.csv")
        ledger.append(
            date=datetime.date(1970, 1, 1),
            product="Transonic Fremules",
            units=1,
            debit=0,
            credit=597,
            balance=-597,
        )
        with open("superpy_ledger.csv", "r", newline="") as ledger:
            assert list(csv.reader(ledger)) == [
                ["date", "product", "units", "debit", "credit", "balance"],
                ["1970-01-01", "Transonic Fremules", "1", "0", "597", "-597"],
            ]

    def test_print(self, capsys, mock_ledger):
        superpy.cli(["report"])
        out, err = capsys.readouterr()
        assert out == (
            "DATE        PRODUCT        UNITS   DEBIT  CREDIT BALANCE\n"
            "1970-01-01  frobule            1       0     150    -150\n"
            "1970-01-01  wobjock           10       0     850    -850\n"
            "1970-01-01  frobulator         5       0    2495   -2495\n"
            "1970-01-01  wobjock           10    4000       0    4000\n"
            "1970-01-01  frobulator         5    5250       0    5250\n"
        )

    def test_balance(self, capsys, mock_ledger):
        superpy.cli(["report", "--balance"])
        out, err = capsys.readouterr()
        assert out == "5755\n"


class TestConfig:
    @pytest.fixture
    def configuration(self):
        return superpy.Config()

    @pytest.mark.parametrize(
        "attr, val", [("date", "1970-01-01"), ("ledger", "superpy_ledger.csv")]
    )
    def test_file_not_found(self, configuration, attr, val):
        assert not os.path.exists(configuration.path)
        assert configuration.get(attr) == val

    @pytest.mark.parametrize(
        "attr, val", [("date", "2020-02-02"), ("ledger", "/tmp/foo")]
    )
    def test_get_set(self, configuration, attr, val):
        configuration.set(attr, val)
        assert configuration.get(attr) == val
