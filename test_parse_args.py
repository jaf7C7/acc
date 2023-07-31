import argparse
import pytest
import superpy


@pytest.mark.parametrize(
    "args, expected",
    [
        (["date"], argparse.Namespace(command="date", date=None, days_to_advance=None)),
        (
            ["date", "2020-02-02"],
            argparse.Namespace(command="date", date="2020-02-02", days_to_advance=None),
        ),
        (
            ["date", "--advance", "1"],
            argparse.Namespace(command="date", date=None, days_to_advance=1),
        ),
        (
            ["date", "--advance"],
            argparse.Namespace(command="date", date=None, days_to_advance=1),
        ),
        (["ledger"], argparse.Namespace(command="ledger", ledger_path=None)),
        (
            ["ledger", "/tmp/foo"],
            argparse.Namespace(command="ledger", ledger_path="/tmp/foo"),
        ),
    ],
)
def test_parse_args(args, expected):
    assert superpy.parse_args(args) == expected
