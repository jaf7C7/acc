import csv
import datetime
from decimal import Decimal
import pytest
from acc import main


@pytest.fixture
def ledger():
    return main.Ledger(main.DEFAULT_LEDGER)


def test_write(ledger):
    ledger.append(
        id=len(ledger),
        date=datetime.date(1970, 1, 1).isoformat(),
        amount='{:+.2f}'.format(Decimal('597')),
        description='Transonic Fremules',
    )
    with open(main.DEFAULT_LEDGER, 'r', newline='') as ledger:
        assert list(csv.reader(ledger)) == [
            ['id', 'date', 'amount', 'description'],
            ['0', '1970-01-01', '+597.00', 'Transonic Fremules'],
        ]
