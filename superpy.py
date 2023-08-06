import datetime
import argparse
import csv


def cli(argv):
    app = Application()
    return app.run(argv)


class daydelta(datetime.timedelta):
    def __new__(cls, days):
        return super().__new__(cls, days=int(days))


class Application:
    def __init__(self):
        self.config = ".superpy.conf"
        self._date = datetime.date(1970, 1, 1)
        self._ledger = "superpy_ledger.csv"

    def read_config(self):
        try:
            with open(self.config, "r") as config:
                date_string, self._ledger = next(csv.reader(config))
            self._date = datetime.date.fromisoformat(date_string)
        except FileNotFoundError:
            pass

    def write_config(self):
        with open(self.config, "w") as config:
            csv.writer(config).writerow([self.date, self.ledger])

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, new_date):
        self._date = new_date
        self.write_config()

    @property
    def ledger(self):
        return self._ledger

    @ledger.setter
    def ledger(self, new_ledger):
        self._ledger = new_ledger
        self.write_config()

    def write_transaction_to_ledger(self, product, amount):
        with open("superpy_ledger.csv", "a") as ledger:
            csv.writer(ledger).writerow([self.date, product, amount])

    def report(self):
        with open(self.ledger, "r") as ledger:
            print(f"{'DATE':10}  {'PRODUCT':10}  AMOUNT")
            for date, product, amount in csv.reader(ledger):
                print(f"{date:10}  {product:10}  {amount}")

    @staticmethod
    def parse_args(argv):
        parser = argparse.ArgumentParser(exit_on_error=False)
        subparsers = parser.add_subparsers(dest="command")

        date_parser = subparsers.add_parser("date", exit_on_error=False)
        date_parser.add_argument(
            "new_date", nargs="?", type=datetime.date.fromisoformat
        )
        date_parser.add_argument(
            "--advance",
            dest="days_to_advance",
            type=daydelta,
            nargs="?",
            const="1",
        )

        ledger_parser = subparsers.add_parser("ledger", exit_on_error=False)
        ledger_parser.add_argument("ledger_path", nargs="?")

        buy_parser = subparsers.add_parser("buy", exit_on_error=False)
        buy_parser.add_argument("product")
        buy_parser.add_argument("amount")

        report_parser = subparsers.add_parser(  # noqa: F841
            "report", exit_on_error=False
        )

        return parser.parse_args(argv)

    def run(self, argv=None):
        self.read_config()
        try:
            args = self.parse_args(argv)
        except argparse.ArgumentError:
            return 1

        if args.command == "date":
            if args.new_date is not None:
                self.date = args.new_date
            elif args.days_to_advance is not None:
                self.date += args.days_to_advance
            else:
                print(self.date)

        elif args.command == "ledger":
            if args.ledger_path is not None:
                self.ledger = args.ledger_path
            else:
                print(self.ledger)

        elif args.command == "buy":
            self.write_transaction_to_ledger(args.product, args.amount)

        elif args.command == "report":
            try:
                self.report()
            except FileNotFoundError:
                return 1

        return 0
