import datetime
import argparse


def get_date():
    try:
        with open(".superpy.conf", "r") as date_file:
            date = date_file.read()
    except FileNotFoundError:
        date = "1970-01-01"
    return date


def write_date(date):
    with open(".superpy.conf", "w") as date_file:
        date_file.write(date)


def parse_args(argv):
    parser = argparse.ArgumentParser(exit_on_error=False)
    subparsers = parser.add_subparsers(dest="command")
    date_parser = subparsers.add_parser("date")
    date_parser.add_argument("date", nargs="?")
    date_parser.add_argument(
        "--advance", dest="days_to_advance", type=int, nargs="?", const=1
    )
    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        return 1
    if argv[0] == "date":
        if len(argv) > 1:
            if argv[1] == "--advance":
                days = int(argv[2]) if len(argv) == 3 else 1
                date = datetime.date.fromisoformat(get_date())
                date += datetime.timedelta(days=days)
                write_date(date.isoformat())
            else:
                write_date(argv[1])
        else:
            date = get_date()
            print(date)
    elif argv[0] == "ledger":
        if len(argv) > 1:
            with open(".superpy.conf", "w") as config:
                config.write(argv[1])
        else:
            try:
                with open(".superpy.conf", "r") as config:
                    ledger = config.read()
            except FileNotFoundError:
                ledger = "superpy_ledger.csv"
            print(ledger)
    return 0
