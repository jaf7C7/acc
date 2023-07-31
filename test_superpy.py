import pytest
import superpy


def test_fails_if_no_args():
    assert superpy.main() == 1
