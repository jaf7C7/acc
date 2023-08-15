import sys
from datetime import date as Date
from datetime import timedelta as TimeDelta
import argparse
import csv


def cli(argv):
    """Handles creating and running an Application instance"""
    app = Application()
    return app.run(argv)


class DayDelta(TimeDelta):
    """A TimeDelta object with a resolution of 1 day"""

    def __new__(cls, days):
        return super().__new__(cls, days=int(days))


class Config:
    """An abstraction of the configuration file"""

    defaults = dict(date="1970-01-01", ledger="superpy_ledger.csv")

    def __init__(self, path=".superpy.conf"):
        self.path = path

    def read(self):
        try:
            with open(self.path, "r", newline="") as f:
                return next(csv.DictReader(f))
        except FileNotFoundError:
            return self.defaults

    def write(self, config):
        with open(self.path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.defaults.keys())
            writer.writeheader()
            writer.writerow(config)

    def get(self, attr):
        return self.read()[attr]

    def set(self, attr, val):
        config = self.read() | {attr: val}
        self.write(config)


class Ledger:
    """A wrapper for reading, writing and processing transaction data in csv format"""

    fieldnames = ["date", "product", "units", "debit", "credit", "balance"]

    def __init__(self, path):
        self.path = path

    def __len__(self):
        return len(list(iter(self)))

    def __str__(self):
        return self.path

    def __eq__(self, other):
        return self.path == other.path

    def __iter__(self):
        with open(self.path, "r", newline="") as f:
            yield from csv.DictReader(f)

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    @staticmethod
    def _format(line):
        """Formats a line in the ledger into a readable form"""
        date, product, units, debit, credit, balance = line
        return f"{date:12}{product:12}{units:>8}{debit:>8}{credit:>8}{balance:>8}"

    def print(self):
        """Print the contents of the ledger in table form"""
        print(self._format(f.upper() for f in self.fieldnames))
        for transaction in self:
            print(self._format(transaction.values()))

    def append(self, **transaction):
        """Writes a transaction to the ledger file"""
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            if len(self) == 0:
                writer.writeheader()
            writer.writerow(transaction)

    def balance(self):
        """Calculates the total balance from all transactions in the ledger"""
        return sum(int(transaction["balance"]) for transaction in self)


class Application:
    """Handles the top-level running of the application"""

    def __init__(self, config_path=".superpy.conf"):
        self.config = Config(config_path)
        self.date = Date.fromisoformat(self.config.get("date"))
        self.ledger = Ledger(self.config.get("ledger"))

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def parse_args(self, argv):
        """Handles parsing, type-checking and casting of command line arguments"""
        parser = argparse.ArgumentParser(exit_on_error=False)
        subparsers = parser.add_subparsers(dest="command")

        date_parser = subparsers.add_parser(
            "date", exit_on_error=False, help="set a new application date"
        )
        date_parser.add_argument(
            "date",
            nargs="?",
            type=Date.fromisoformat,
            metavar="<date>",
            help="a date in yyyy-mm-dd iso format",
        )
        date_parser.add_argument(
            "--advance",
            dest="days",
            type=DayDelta,
            nargs="?",
            const="1",
            metavar="<days>",
            help="the number of days to advance (default %(const)s day)",
        )

        ledger_parser = subparsers.add_parser(
            "ledger", exit_on_error=False, help="select a new ledger file"
        )
        ledger_parser.add_argument(
            "ledger",
            type=Ledger,
            nargs="?",
            metavar="<ledger>",
            help="the path to the new ledger file",
        )

        buy_parser = subparsers.add_parser(
            "buy", exit_on_error=False, help="record a purchase in the ledger"
        )
        buy_parser.add_argument(
            "product", metavar="<product>", help="the name of the product to be bought"
        )
        buy_parser.add_argument(
            "price", type=int, metavar="<price>", help="the product price in cents"
        )
        buy_parser.add_argument(
            "--units",
            default="1",
            type=int,
            metavar="<units>",
            help="how many units to buy (default %(default)s)",
        )

        sell_parser = subparsers.add_parser(
            "sell", exit_on_error=False, help="record a sale in the ledger"
        )
        sell_parser.add_argument(
            "product", metavar="<product>", help="the name of the product to be sold"
        )
        sell_parser.add_argument(
            "price", type=int, metavar="<price>", help="the product price in cents"
        )
        sell_parser.add_argument(
            "--units",
            default="1",
            type=int,
            metavar="<units>",
            help="how many units to sell (default %(default)s)",
        )

        report_parser = subparsers.add_parser(
            "report",
            exit_on_error=False,
            help="display information about past transactions",
        )
        report_parser.add_argument(
            "--balance",
            action="store_true",
            help="the net value of ledger transactions",
        )

        return parser.parse_args(argv)

    def run(self, argv=None):
        """Run the program with the given arguments"""
        try:
            args = self.parse_args(argv)
        except argparse.ArgumentError as err:
            print(err, file=sys.stderr)
            return 1

        if args.command == "date":
            if args.date is not None:
                self.date = args.date
                self.config.set("date", self.date)
            elif args.days is not None:
                self.date += args.days
                self.config.set("date", self.date)
            else:
                print(self.date)

        elif args.command == "ledger":
            if args.ledger is not None:
                self.ledger = args.ledger
                self.config.set("ledger", self.ledger)
            else:
                print(self.ledger)

        elif args.command in {"buy", "sell"}:
            debit = args.price * args.units if args.command == "sell" else 0
            credit = args.price * args.units if args.command == "buy" else 0
            self.ledger.append(
                date=self.date,
                product=args.product,
                units=args.units,
                debit=debit,
                credit=credit,
                balance=(debit - credit),
            )

        elif args.command == "report":
            if args.balance is True:
                print(self.ledger.balance())
            else:
                self.ledger.print()
