import argparse
import superpy


def test_sets_command_attribute():
    assert superpy.parse_args(["date"]) == argparse.Namespace(command="date")
