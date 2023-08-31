import csv
import os
import pytest
from acc import main


@pytest.fixture(autouse=True)
def temp_dir(tmp_path):
    os.chdir(tmp_path)
    yield
    for file in main.CONFIG_PATH, main.LEDGER_PATH:
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


@pytest.fixture
def mock_ledger():
    ledger = [
        ["id", "date", "amount", "type", "description"],
        ["0", "1970-01-01", "2495.00", "credit", "foo"],
        ["1", "1970-02-02", "5250.00", "debit", "qux"],
        ["2", "1970-03-03", "600.00", "debit", "frobulant"],
    ]
    with open(main.LEDGER_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        for transaction in ledger:
            writer.writerow(transaction)