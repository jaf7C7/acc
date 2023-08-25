import sys
import argparse
import csv
import datetime
from decimal import Decimal
from typing import Union, Sequence, Generator, Iterable


CONFIG_PATH = ".acc.conf"
LEDGER_PATH = "acc_ledger.csv"


def cli(argv) -> int:
    """Handles creating and running an Application instance"""
    app = Application()
    return app.run(argv)


def parse_args(argv: Union[Sequence[str], None] = None) -> argparse.Namespace:
    """Handles parsing, type-checking and casting of command line arguments"""
    parser = argparse.ArgumentParser(exit_on_error=False)
    subparsers = parser.add_subparsers(dest="command")

    date_parser = subparsers.add_parser(
        "date", exit_on_error=False, help="set a new application date"
    )
    date_parser.add_argument(
        "date",
        nargs="?",
        type=datetime.date.fromisoformat,
        metavar="<date>",
        help="a date in yyyy-mm-dd iso format",
    )
    date_parser.add_argument(
        "--advance",
        dest="days",
        type=daydelta,  # type: ignore [arg-type]
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

    credit_parser = subparsers.add_parser(
        "credit", exit_on_error=False, help="record a credit transaction in the ledger"
    )
    credit_parser.add_argument(
        "amount",
        metavar="<amount>",
        type=Decimal,
        help="the amount to be credited",
    )
    credit_parser.add_argument(
        "--description",
        "-d",
        metavar="<description>",
        help="a short description of the transation",
    )

    debit_parser = subparsers.add_parser(
        "debit", exit_on_error=False, help="record a debit transaction in the ledger"
    )
    debit_parser.add_argument(
        "amount",
        metavar="<amount>",
        type=Decimal,
        help="the amount to be debited",
    )
    debit_parser.add_argument(
        "--description",
        "-d",
        metavar="<description>",
        help="a short description of the transation",
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

    if not argv:
        argv = ["--help"]
    return parser.parse_args(argv)


class daydelta(datetime.timedelta):
    """A datetime.timedelta object with a resolution of 1 day"""

    resolution = datetime.timedelta(days=1)

    def __new__(cls, days: int) -> datetime.timedelta:  # type: ignore [misc]
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

    # field: format-spec
    fields = {
        "id": "{:8}",
        "date": "{:12}",
        "amount": "{:10}",
        "type": "{:8}",
        "description": "{}",
    }

    def __init__(self, path: str) -> None:
        self.path = path

    def __str__(self):
        return self.path

    def __len__(self) -> int:
        try:
            return len(list(iter(self)))
        except FileNotFoundError:
            return 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Ledger) and self.path == other.path

    def __iter__(self) -> Generator[dict[str, str], None, None]:
        with open(self.path, "r", newline="") as f:
            yield from csv.DictReader(f)

    @property
    def balance(self) -> int:
        """Calculates the total balance from all transactions in the ledger"""
        return sum(
            Decimal(transaction["amount"])  # type: ignore[misc]
            if transaction["type"] == "debit"
            else -Decimal(transaction["amount"])
            for transaction in self
        )

    def collimate(self, transaction: Iterable[str]) -> str:
        """Format a line in the file into a readable form"""
        return "".join(self.fields.values()).format(*transaction)

    def tabulate(self) -> Generator[Sequence[str], None, None]:
        """A generator yielding formatted rows of the ledger contents"""
        yield self.collimate(self.fields.keys()).upper()
        for transaction in self:
            yield self.collimate(transaction.values())

    def append(self, **transaction: Union[str, int]) -> None:
        """Writes a transaction to the ledger file"""
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields.keys())
            if len(self) == 0:
                writer.writeheader()
            writer.writerow(transaction)


class Application(_AttributeHolder):
    """Handles the top-level running of the application"""

    def __init__(self, config: str = CONFIG_PATH) -> None:
        self.config = config
        self.date = datetime.date(1970, 1, 1)
        self.ledger = Ledger(LEDGER_PATH)

    def read_config(self) -> None:
        """Update application properties with values from the config file"""
        try:
            with open(self.config, "r", newline="") as f:
                config = next(csv.DictReader(f))
        except FileNotFoundError:
            pass
        else:
            self.date = datetime.date.fromisoformat(config["date"])
            self.ledger = Ledger(config["ledger"])

    def write_config(self) -> None:
        """Write key/value pairs to the config file"""
        with open(self.config, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "ledger"])
            writer.writeheader()
            writer.writerow(dict(date=self.date, ledger=self.ledger))

    def run(self, argv: Union[Sequence[str], None] = None) -> int:
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

        elif args.command in {"debit", "credit"}:
            self.ledger.append(
                id=len(self.ledger),
                date=self.date.isoformat(),
                type=args.command,
                amount="{:.2f}".format(args.amount),
                description=args.description,
            )

        elif args.command == "report":
            if args.balance is True:
                print("{:.2f}".format(self.ledger.balance))
            else:
                for row in self.ledger.tabulate():
                    print(row)

        return 0
