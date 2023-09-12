import csv
import pytest
from acc import cli, main


def test_date_without_args_prints_the_default_date(capsys):
    cli.main(['date'])
    out, err = capsys.readouterr()
    assert out.strip() == main.DEFAULT_DATE.isoformat()


def test_can_set_and_get_the_date(capsys):
    cli.main(['date', '2020-02-02'])
    cli.main(['date'])
    out, err = capsys.readouterr()
    assert out == '2020-02-02\n'


def test_fails_if_non_iso_format_date():
    assert cli.main(['date', '01/01/1970']) == 1


@pytest.mark.parametrize(
    'days, expected',
    [('', '1970-01-02\n'), ('366', '1971-01-02\n')],
)
def test_can_advance_date_by_days(capsys, days, expected):
    cli.main(['date', '1970-01-01'])
    cli.main(f'date --advance {days}'.split())
    cli.main(['date'])
    out, err = capsys.readouterr()
    assert out == expected


def test_fails_if_non_integer_days():
    assert cli.main(['date', '--advance', '0.5']) == 1


def test_ledger_without_args_prints_the_default_ledger(capsys):
    cli.main(['ledger'])
    out, err = capsys.readouterr()
    assert out == 'acc_ledger.csv\n'


def test_date_and_ledger_can_be_set_independently(capsys):
    cli.main(['date', '1991-08-20'])
    cli.main(['ledger', '/tmp/foo'])
    cli.main(['date'])
    cli.main(['ledger'])
    out, err = capsys.readouterr()
    assert out.split() == ['1991-08-20', '/tmp/foo']


def test_can_set_and_get_the_ledger(capsys):
    cli.main(['ledger', '/tmp/foo'])
    cli.main(['ledger'])
    out, err = capsys.readouterr()
    assert out == '/tmp/foo\n'


def test_can_record_transactions(capsys):
    cli.main(['credit', '850', '-d', 'apple'])
    cli.main(['debit', '500', '--description', 'apple'])
    with open(main.DEFAULT_LEDGER, 'r', newline='') as ledger:
        assert list(csv.reader(ledger)) == [
            ['id', 'date', 'amount', 'description'],
            ['0', main.DEFAULT_DATE.isoformat(), '-850.00', 'apple'],
            ['1', main.DEFAULT_DATE.isoformat(), '+500.00', 'apple'],
        ]


def test_report_prints_transactions_up_to_current_date(capsys, mock_ledger):
    cli.main(['report'])
    out, err = capsys.readouterr()
    assert out == (
        'ID      DATE          AMOUNT  DESCRIPTION\n'
        '0       1970-01-01  -2495.00  foo\n'
    )


def test_can_report_on_a_single_date(capsys, mock_ledger):
    cli.main(['report', '1970-02-02'])
    out, err = capsys.readouterr()
    assert out == (
        'ID      DATE          AMOUNT  DESCRIPTION\n'
        '1       1970-02-02  +5250.00  qux\n'
    )


def test_can_report_over_a_range_of_dates(capsys, mock_ledger):
    cli.main(['report', '1970-01-01~1970-03-01'])
    out, err = capsys.readouterr()
    assert out == (
        'ID      DATE          AMOUNT  DESCRIPTION\n'
        '0       1970-01-01  -2495.00  foo\n'
        '1       1970-02-02  +5250.00  qux\n'
    )


def test_can_report_over_a_range_of_dates_with_first_date_omitted(capsys, mock_ledger):
    cli.main(['report', '~1970-03-03'])
    out, err = capsys.readouterr()
    assert out == (
        'ID      DATE          AMOUNT  DESCRIPTION\n'
        '0       1970-01-01  -2495.00  foo\n'
        '1       1970-02-02  +5250.00  qux\n'
        '2       1970-03-03   +600.00  frobulant\n'
    )


def test_report_over_a_range_of_dates_with_last_date_omitted(capsys, mock_ledger):
    cli.main(['report', '1970-02-01~'])
    out, err = capsys.readouterr()
    assert out == (
        'ID      DATE          AMOUNT  DESCRIPTION\n'
        '1       1970-02-02  +5250.00  qux\n'
        '2       1970-03-03   +600.00  frobulant\n'
    )


def test_balance_calculates_correct_balance(capsys, mock_ledger):
    cli.main(['date', '1970-04-01'])
    cli.main(['balance'])
    out, err = capsys.readouterr()
    assert out == '+3355.00\n'
