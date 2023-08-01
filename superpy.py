import sys
import os.path
import datetime
import argparse


def get_config():
    try:
        with open(".superpy.conf", "r") as c:
            config = dict(zip(["date", "ledger"], c.read().split()))
    except FileNotFoundError:
        config = dict(date="1970-01-01", ledger="superpy_ledger.csv")
    return config


def set_config(key, value):
    config = get_config()
    config.update({key: value})
    with open(".superpy.conf", "w") as c:
        c.write("\t".join(config.values()))


def advance_date(days_to_advance):
    date = datetime.date.fromisoformat(get_config().get("date"))
    days = datetime.timedelta(days=days_to_advance)
    new_date = date + days
    set_config("date", new_date.isoformat())


def create_if_not_exists(ledger_path):
    if not os.path.exists(ledger_path):
        open(ledger_path, "x").close()


def write_transaction_to_ledger(product, amount):
    with open("superpy_ledger.csv", "a") as ledger:
        fields = [get_config().get("date"), product, amount]
        ledger.write("\t".join(fields) + "\n")


def report(ledger_path):
    try:
        with open(ledger_path, "r") as ledger:
            print("\t".join(["DATE", "PRODUCT", "AMOUNT"]))
            print(ledger.read(), end="")
    except FileNotFoundError:
        pass


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
            set_config("date", args.date.isoformat())
        elif args.days_to_advance is not None:
            advance_date(args.days_to_advance)
        else:
            print(get_config().get("date"))
    elif args.command == "ledger":
        if args.ledger_path is not None:
            set_config("ledger", args.ledger_path)
        else:
            print(get_config().get("ledger"))
    elif args.command == "buy":
        create_if_not_exists("superpy_ledger.csv")
        write_transaction_to_ledger(args.product, args.amount)
    elif args.command == "report":
        report(get_config().get("ledger"))
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
