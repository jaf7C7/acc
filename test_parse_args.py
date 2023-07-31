import argparse
import pytest
import superpy


@pytest.mark.parametrize(
    "args, expected",
    [
        (["date"], argparse.Namespace(command="date", date=None)),
        (["date", "2020-02-02"], argparse.Namespace(command="date", date="2020-02-02")),
    ],
)
def test_parse_args(args, expected):
    assert superpy.parse_args(args) == expected
