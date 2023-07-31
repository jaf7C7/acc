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
    ],
)
def test_parse_args(args, expected):
    assert superpy.parse_args(args) == expected
