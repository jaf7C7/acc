import superpy


def test_returns_1_if_no_args():
    assert superpy.main() == 1


def test_returns_0_if_args():
    assert superpy.main(["frobble"]) == 0


def test_date_without_args_prints_the_default_date(capsys):
    superpy.main(["date"])
    out, err = capsys.readouterr()
    assert out == "1970-01-01\n"
