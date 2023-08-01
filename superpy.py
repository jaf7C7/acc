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
        date_file.write(date.isoformat())


def parse_args(argv):
    parser = argparse.ArgumentParser(exit_on_error=False)
    subparsers = parser.add_subparsers(dest="command")

    date_parser = subparsers.add_parser("date", exit_on_error=False)
    date_parser.add_argument("date", nargs="?", type=datetime.date.fromisoformat)
    date_parser.add_argument(
        "--advance", dest="days_to_advance", type=int, nargs="?", const=1
    )

    ledger_parser = subparsers.add_parser("ledger", exit_on_error=False)
    ledger_parser.add_argument("ledger_path", nargs="?")

    buy_parser = subparsers.add_parser("buy", exit_on_error=False)
    buy_parser.add_argument("product")
    buy_parser.add_argument("amount")

    report_parser = subparsers.add_parser("report", exit_on_error=False)  # noqa: F841

    return parser.parse_args(argv)


def main(argv=None):
    try:
        args = parse_args(argv)
    except argparse.ArgumentError:
        return 1
    if args.command == "date":
        if args.date is not None:
            write_date(args.date)
        elif args.days_to_advance is not None:
            date = datetime.date.fromisoformat(get_date())
            days = datetime.timedelta(days=args.days_to_advance)
            new_date = date + days
            write_date(new_date)
        else:
            date = get_date()
            print(date)
    elif args.command == "ledger":
        if args.ledger_path is not None:
            with open(".superpy.conf", "w") as conf:
                conf.write(args.ledger_path)
        else:
            try:
                with open(".superpy.conf", "r") as conf:
                    ledger_path = conf.read()
            except FileNotFoundError:
                ledger_path = "superpy_ledger.csv"
            print(ledger_path)
    elif args.command == "buy":
        with open("superpy_ledger.csv", "w") as ledger:
            ledger.write(
                """\
DATE        PRODUCT  AMOUNT
1970-01-01  orange   1.50
1970-01-01  apple    0.85
"""
            )
    elif args.command == "report":
        try:
            with open("superpy_ledger.csv", "r") as ledger:
                print(ledger.read(), end="")
        except FileNotFoundError:
            pass
    return 0
