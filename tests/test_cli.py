import os
import csv
import pytest
from acc import cli


CONFIG_PATH = ".acc.conf"
LEDGER_PATH = "acc_ledger.csv"


@pytest.fixture(autouse=True)
def temp_dir(tmp_path):
    os.chdir(tmp_path)
    yield
    for file in CONFIG_PATH, LEDGER_PATH:
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


@pytest.fixture
def mock_ledger():
    ledger = [
        ["id", "date", "amount", "type", "description"],
        ["0", "1970-01-01", "2495.00", "credit", "frobulator"],
        ["1", "1970-01-01", "5250.00", "debit", "frobulator"],
    ]
    with open(LEDGER_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        for transaction in ledger:
            writer.writerow(transaction)


def test_date_without_args_prints_the_default_date(capsys):
    cli.main(["date"])
    out, err = capsys.readouterr()
    assert out == "1970-01-01\n"


def test_can_set_and_get_the_date(capsys):
    cli.main(["date", "2020-02-02"])
    cli.main(["date"])
    out, err = capsys.readouterr()
    assert out == "2020-02-02\n"


def test_fails_if_non_iso_format_date():
    assert cli.main(["date", "01/01/1970"]) == 1


@pytest.mark.parametrize(
    "days, expected",
    [("", "1970-01-02\n"), ("366", "1971-01-02\n")],
)
def test_can_advance_date_by_days(capsys, days, expected):
    cli.main(f"date --advance {days}".split())
    cli.main(["date"])
    out, err = capsys.readouterr()
    assert out == expected


def test_fails_if_non_integer_days():
    assert cli.main(["date", "--advance", "0.5"]) == 1


def test_ledger_without_args_prints_the_default_ledger(capsys):
    cli.main(["ledger"])
    out, err = capsys.readouterr()
    assert out == "acc_ledger.csv\n"


def test_date_and_ledger_can_be_set_independently(capsys):
    cli.main(["date", "1991-08-20"])
    cli.main(["ledger", "/tmp/foo"])
    cli.main(["date"])
    cli.main(["ledger"])
    out, err = capsys.readouterr()
    assert out.split() == ["1991-08-20", "/tmp/foo"]


def test_can_set_and_get_the_ledger(capsys):
    cli.main(["ledger", "/tmp/foo"])
    cli.main(["ledger"])
    out, err = capsys.readouterr()
    assert out == "/tmp/foo\n"


def test_can_record_transactions(capsys):
    cli.main(["credit", "850", "-d", "apple"])
    cli.main(["debit", "500", "--description", "apple"])
    with open(LEDGER_PATH, "r", newline="") as ledger:
        assert list(csv.reader(ledger)) == [
            ["id", "date", "amount", "type", "description"],
            ["0", "1970-01-01", "850.00", "credit", "apple"],
            ["1", "1970-01-01", "500.00", "debit", "apple"],
        ]


def test_report(capsys, mock_ledger):
    cli.main(["report"])
    out, err = capsys.readouterr()
    assert out == (
        "ID      DATE        AMOUNT    TYPE    DESCRIPTION\n"
        "0       1970-01-01  2495.00   credit  frobulator\n"
        "1       1970-01-01  5250.00   debit   frobulator\n"
    )


def test_balance(capsys, mock_ledger):
    cli.main(["report", "--balance"])
    out, err = capsys.readouterr()
    assert out == "2755.00\n"
