import argparse
import pytest
import superpy


@pytest.mark.parametrize(
    "args, expected",
    [
        (["date"], argparse.Namespace(command="date")),
    ],
)
def test_parse_args(args, expected):
    assert superpy.parse_args(args) == expected
