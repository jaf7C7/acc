import argparse
import datetime
import pytest
import superpy


@pytest.mark.parametrize(
    "args, expected",
    [
        (["date"], argparse.Namespace(command="date", date=None, days_to_advance=None)),
        (
            ["date", "2020-02-02"],
            argparse.Namespace(
                command="date", date=datetime.date(2020, 2, 2), days_to_advance=None
            ),
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
        (
            ["buy", "orange", "1.5"],
            argparse.Namespace(command="buy", product="orange", amount="1.5"),
        ),
    ],
)
def test_parse_args(args, expected):
    assert superpy.parse_args(args) == expected


@pytest.mark.parametrize("args", [["date", "01/01/1970"], ["date", "--advance", "0.5"]])
def test_bad_arguments(args):
    with pytest.raises(argparse.ArgumentError):
        superpy.parse_args(args)
