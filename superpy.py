import sys


def main(argv=None):
    if argv is None:
        return 1
    if argv[0] == "date":
        print("1970-01-01")
