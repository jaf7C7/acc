import os
import csv
import datetime
from decimal import Decimal
import pytest
from acc import main


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
def ledger():
    return main.Ledger(LEDGER_PATH)


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


def test_write(ledger):
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
