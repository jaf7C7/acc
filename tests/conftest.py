import csv
import os
import pytest
from acc import main


@pytest.fixture(autouse=True)
def temp_dir(tmp_path):
    os.chdir(tmp_path)
    yield
    for file in main.DEFAULT_CONFIG, main.DEFAULT_LEDGER:
        try:
            os.unlink(file)
        except FileNotFoundError:
            pass


@pytest.fixture
def mock_ledger():
    ledger = [
        ['id', 'date', 'amount', 'description'],
        ['0', '1970-01-01', '-2495.00', 'foo'],
        ['1', '1970-02-02', '+5250.00', 'qux'],
        ['2', '1970-03-03', '+600.00', 'frobulant'],
    ]
    with open(main.DEFAULT_LEDGER, 'w', newline='') as f:
        writer = csv.writer(f)
        for transaction in ledger:
            writer.writerow(transaction)
