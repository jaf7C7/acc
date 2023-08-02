import datetime
import argparse
import csv


def get_config(param=None):
    try:
        with open(".superpy.conf", "r") as c:
            config = dict(zip(["date", "ledger"], next(csv.reader(c))))
    except FileNotFoundError:
        config = dict(date="1970-01-01", ledger="superpy_ledger.csv")
    return config.get(param) if param is not None else config


def set_config(key, value):
    config = get_config()
    config.update({key: value})
    with open(".superpy.conf", "w") as c:
        csv.writer(c).writerow(config.values())


def advance_date(days_to_advance):
    date = datetime.date.fromisoformat(get_config("date"))
    days = datetime.timedelta(days=days_to_advance)
    new_date = date + days
    set_config("date", new_date.isoformat())


def write_transaction_to_ledger(product, amount):
    with open("superpy_ledger.csv", "a") as ledger:
        csv.writer(ledger).writerow([get_config("date"), product, amount])


def report(ledger_path):
    with open(ledger_path, "r") as ledger:
        print(f"{'DATE':10}  {'PRODUCT':10}  AMOUNT")
        for date, product, amount in csv.reader(ledger):
            print(f"{date:10}  {product:10}  {amount}")


def parse_args(argv):
    parser = argparse.ArgumentParser(exit_on_error=False)
    subparsers = parser.add_subparsers(dest="command")

    date_parser = subparsers.add_parser("date", exit_on_error=False)
    date_parser.add_argument("new_date", nargs="?", type=datetime.date.fromisoformat)
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
        if args.new_date is not None:
            set_config("date", args.new_date.isoformat())
        elif args.days_to_advance is not None:
            advance_date(args.days_to_advance)
        else:
            print(get_config("date"))

    elif args.command == "ledger":
        if args.ledger_path is not None:
            set_config("ledger", args.ledger_path)
        else:
            print(get_config("ledger"))

    elif args.command == "buy":
        write_transaction_to_ledger(args.product, args.amount)

    elif args.command == "report":
        try:
            report(get_config("ledger"))
        except FileNotFoundError:
            return 1

    return 0
