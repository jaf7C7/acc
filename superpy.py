import sys
from datetime import date as Date
from datetime import timedelta as TimeDelta
import argparse
import csv
from typing import Iterable, Union


def cli(argv) -> None:
    """Handles creating and running an Application instance"""
    app = Application()
    return app.run(argv)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
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


class DayDelta(TimeDelta):
    """A TimeDelta object with a resolution of 1 day"""

    resolution = TimeDelta(days=1)

    def __new__(cls, days: int) -> TimeDelta:
        return super().__new__(cls, days=int(days))


class _AttributeHolder:
    """Base class to define __repr__ for all subclasses"""

    def __repr__(self) -> str:
        return "%s(%s)" % (
            self.__class__.__name__,
            ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items()),
        )


class Ledger(_AttributeHolder):
    """A wrapper for reading, writing and processing transaction data in csv format"""

    fields = {  # field: field-format
        "date": "{:12}",
        "product": "{:12}",
        "units": "{:>8}",
        "debit": "{:>8}",
        "credit": "{:>8}",
        "balance": "{:>8}",
    }

    def __init__(self, path: str) -> None:
        self.path = path

    def __str__(self):
        return self.path

    def __len__(self) -> int:
        return len(list(iter(self)))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Ledger) and self.path == other.path

    def __iter__(self) -> Iterable[dict]:
        with open(self.path, "r", newline="") as f:
            yield from csv.DictReader(f)

    @property
    def balance(self) -> int:
        """Calculates the total balance from all transactions in the ledger"""
        return sum(int(transaction["balance"]) for transaction in self)

    def collimate(self, transaction: Iterable[str]) -> str:
        """Format a line in the file into a readable form"""
        return "".join(self.fields.values()).format(*transaction)

    def tabulate(self) -> Iterable[str]:
        """A generator yielding formatted rows of the ledger contents"""
        yield self.collimate(self.fields.keys()).upper()
        for transaction in self:
            yield self.collimate(transaction.values())

    def append(self, **transaction: dict[str, Union[str, int]]) -> None:
        """Writes a transaction to the ledger file"""
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields.keys())
            if len(self) == 0:
                writer.writeheader()
            writer.writerow(transaction)


class Application(_AttributeHolder):
    """Handles the top-level running of the application"""

    def __init__(self, config: str = ".superpy.conf") -> None:
        self.config = config
        self.date = Date(1970, 1, 1)
        self.ledger = Ledger("superpy_ledger.csv")

    def read_config(self) -> None:
        """Update application properties with values from the config file"""
        try:
            with open(self.config, "r", newline="") as f:
                config = next(csv.DictReader(f))
        except FileNotFoundError:
            pass
        else:
            self.date = Date.fromisoformat(config["date"])
            self.ledger = Ledger(config["ledger"])

    def write_config(self) -> None:
        """Write key/value pairs to the config file"""
        with open(self.config, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "ledger"])
            writer.writeheader()
            writer.writerow(dict(date=self.date, ledger=self.ledger))

    def run(self, argv: Iterable[str] = None) -> int:
        """Run the program with the given arguments"""
        self.read_config()
        try:
            args = parse_args(argv)
        except argparse.ArgumentError as err:
            print(err, file=sys.stderr)
            return 1

        if args.command == "date":
            if args.date is not None:
                self.date = args.date
                self.write_config()
            elif args.days is not None:
                self.date += args.days
                self.write_config()
            else:
                print(self.date.isoformat())

        elif args.command == "ledger":
            if args.ledger is not None:
                self.ledger = args.ledger
                self.write_config()
            else:
                print(self.ledger.path)

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
                print(self.ledger.balance)
            else:
                for row in self.ledger.tabulate():
                    print(row)
