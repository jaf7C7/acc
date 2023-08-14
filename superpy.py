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
        return sum(int(transaction["balance"]) for transaction in self.transactions())


class Application:
    """Handles the top-level running of the application"""

    def __init__(self, config_path=".superpy.conf"):
        self.config = config_path
        self._date = Date(1970, 1, 1)
        self._ledger = Ledger("superpy_ledger.csv")
        self.read_config()

    def __repr__(self):
        attrs = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        if not isinstance(date, Date):
            date = Date.fromisoformat(date)
        self._date = date
        self.write_config()

    @property
    def ledger(self):
        return self._ledger

    @ledger.setter
    def ledger(self, ledger):
        if not isinstance(ledger, Ledger):
            ledger = Ledger(ledger)
        self._ledger = ledger
        self.write_config()

    def read_config(self):
        """Set application attributes from the configuration file"""
        try:
            with open(self.config, "r", newline="") as f:
                self.date, self.ledger = next(csv.reader(f))
        except FileNotFoundError:
            pass

    def write_config(self):
        """Write application attributes to the configuration file"""
        with open(self.config, "w", newline="") as f:
            csv.writer(f).writerow([self.date, self.ledger])

    def date_cmd(self, args):
        if args.date is not None:
            self.date = args.date
        elif args.days is not None:
            self.date += args.days
        else:
            print(self.date)

    def ledger_cmd(self, args):
        if args.ledger is not None:
            self.ledger = args.ledger
        else:
            print(self.ledger)

    def sell_cmd(self, args):
        self.ledger.append(
            date=self.date,
            product=args.product,
            units=args.units,
            debit=(args.price * args.units),
            credit=0,
            balance=(args.price * args.units),
        )

    def buy_cmd(self, args):
        self.ledger.append(
            date=self.date,
            product=args.product,
            units=args.units,
            debit=0,
            credit=(args.price * args.units),
            balance=-(args.price * args.units),
        )

    def report_cmd(self, args):
        if args.balance is True:
            print(self.ledger.balance())
        else:
            self.ledger.print()

    def parse_args(self, argv):
        """Handles parsing, type-checking and casting of command line arguments"""
        parser = argparse.ArgumentParser(exit_on_error=False)
        subparsers = parser.add_subparsers()

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
        date_parser.set_defaults(func=self.date_cmd)

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
        ledger_parser.set_defaults(func=self.ledger_cmd)

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
        buy_parser.set_defaults(func=self.buy_cmd)

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
        sell_parser.set_defaults(func=self.sell_cmd)

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
        report_parser.set_defaults(func=self.report_cmd)

        return parser.parse_args(argv)

    def run(self, argv=None):
        """Run the program with the given arguments"""
        try:
            args = self.parse_args(argv)
        except argparse.ArgumentError as err:
            print(err, file=sys.stderr)
            return 1

        args.func(args)
