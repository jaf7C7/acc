import sys
import datetime
from datetime import date as Date
import argparse
import csv


def cli(argv):
    """Handles creating and running an Application instance"""
    app = Application()
    return app.run(argv)


class DayDelta(datetime.timedelta):
    """A datetime.timedelta object with a resolution of 1 day"""

    def __new__(cls, days):
        return super().__new__(cls, days=int(days))


class Config:
    """A wrapper for reading and writing a configuration file in csv format"""

    def __init__(self, path):
        self.path = path
        self.defaults = "1970-01-01", "superpy_ledger.csv"

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def read(self):
        """Read csv data from the configuration file"""
        try:
            with open(self.path, "r", newline="") as f:
                return next(csv.reader(f))
        except FileNotFoundError:
            return self.defaults

    def write(self, attrs):
        """Write csv data to the configuration file"""
        with open(self.path, "w", newline="") as f:
            csv.writer(f).writerow(attrs)


class Ledger:
    """A wrapper for reading, writing and processing transaction data in csv format"""

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path

    def __len__(self):
        return len(list(iter(self)))

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def __eq__(self, other):
        return self.path == other.path

    def __iter__(self):
        with open(self.path, "r", newline="") as f:
            yield from csv.reader(f)

    @staticmethod
    def format(line):
        """Formats a line in the ledger into a readable form"""
        date, product, units, debit, credit, balance = line
        return f"{date:12}{product:12}{units:>8}{debit:>8}{credit:>8}{balance:>8}"

    def print(self):
        """Print the contents of the ledger in table form"""
        ledger = iter(self)
        header = next(ledger)
        print(self.format(field.upper() for field in header))
        for line in ledger:
            print(self.format(line))

    def append(self, **transaction):
        """Writes a transaction to the ledger file"""
        with open(self.path, "a", newline="") as f:
            if len(self) == 0:
                csv.writer(f).writerow(transaction.keys())
            csv.writer(f).writerow(transaction.values())

    def transactions(self):
        """A generator which yields transactions from the ledger file"""
        ledger = iter(self)
        fieldnames = next(ledger)
        yield from (dict(zip(fieldnames, fields)) for fields in ledger)  # noqa: B905

    def balance(self):
        """Calculates the total balance from all transactions in the ledger"""
        try:
            return sum(int(transaction["balance"]) for transaction in self.transactions())
        except FileNotFoundError:
            return 0


class Application:
    """Handles the top-level running of the application"""

    def __init__(self, config_path=".superpy.conf"):
        self.config = Config(config_path)
        date_string, ledger_path = self.config.read()
        self.date = Date.fromisoformat(date_string)
        self.ledger = Ledger(ledger_path)

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    @staticmethod
    def parse_args(argv):
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
            action="store_const",
            const="balance",
            dest="report_type",
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
                self.config.write([self.date, self.ledger])
            elif args.days is not None:
                self.date += args.days
                self.config.write([self.date, self.ledger])

            else:
                print(self.date)

        elif args.command == "ledger":
            if args.ledger is not None:
                self.ledger = args.ledger
                self.config.write([self.date, self.ledger])
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
            if args.report_type == "balance":
                print(self.ledger.balance())
            else:
                self.ledger.print()
        return 0
