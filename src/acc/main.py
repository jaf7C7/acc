import sys
import argparse
import csv
import datetime
from decimal import Decimal
from typing import Union, Sequence, Generator, Iterable


# TODO: Get rid of global variables
DEFAULT_CONFIG = '.acc.conf'
DEFAULT_LEDGER = 'acc_ledger.csv'
# TODO: Why is default date a date object and default ledger a string?
DEFAULT_DATE = datetime.date(1970, 1, 1)
MIN_DATE = datetime.date(datetime.MINYEAR, 1, 1)
MAX_DATE = datetime.date(datetime.MAXYEAR, 12, 31)


class daydelta(datetime.timedelta):
    """A datetime.timedelta object with a resolution of 1 day"""

    resolution = datetime.timedelta(days=1)

    def __new__(cls, days: int) -> datetime.timedelta:  # type: ignore [misc]
        return super().__new__(cls, days=int(days))


class DateSpecAction(argparse.Action):
    """Parses the datespec string into starting and ending dates"""

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            start, end = values.split('~')
        except ValueError:
            start = end = values
        start = datetime.date.fromisoformat(start) if start != '' else MIN_DATE
        end = datetime.date.fromisoformat(end) if end != '' else MAX_DATE
        setattr(namespace, self.dest, [start, end])


class _AttributeHolder:
    """Base class to define __repr__ for all subclasses"""

    def __repr__(self) -> str:
        return '%s(%s)' % (
            self.__class__.__name__,
            ', '.join(f'{k}={repr(v)}' for k, v in self.__dict__.items()),
        )


class Ledger(_AttributeHolder):
    """A wrapper for reading, writing and processing transaction data in csv format"""

    # field: format-spec
    fields = {
        'id': '{:6}',
        'date': '{:10}',
        'amount': '{:>8}',
        'description': '{}',
    }

    def __init__(self, path: str) -> None:
        self.path = path

    def __str__(self) -> str:
        return self.path

    def __len__(self) -> int:
        try:
            return len(list(iter(self)))
        except FileNotFoundError:
            return 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Ledger) and self.path == other.path

    def __iter__(self) -> Generator[dict[str, str], None, None]:
        with open(self.path, 'r', newline='') as f:
            yield from csv.DictReader(f)

    def balance(
        self, start: datetime.date = MIN_DATE, end: datetime.date = MAX_DATE
    ) -> int:
        """Calculates the total balance from all transactions in the ledger"""
        return sum(
            Decimal(transaction['amount'])  # type: ignore[misc]
            for transaction in self
            if start <= datetime.date.fromisoformat(transaction['date']) <= end
        )

    def collimate(self, transaction: Iterable[str]) -> str:
        """Format a line in the file into a readable form"""
        return '  '.join(self.fields.values()).format(*transaction)

    # TODO: 'tabulate' should not be a generator, just let it print lines
    def tabulate(
        self, start: datetime.date = MIN_DATE, end: datetime.date = MAX_DATE
    ) -> Generator[Sequence[str], None, None]:
        """A generator yielding formatted rows of the ledger contents"""
        yield self.collimate(self.fields.keys()).upper()
        for transaction in self:
            if start <= datetime.date.fromisoformat(transaction['date']) <= end:
                yield self.collimate(transaction.values())

    def append(self, **transaction: Union[str, int]) -> None:
        """Writes a transaction to the ledger file"""
        with open(self.path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields.keys())
            if len(self) == 0:
                writer.writeheader()
            writer.writerow(transaction)


class Application(_AttributeHolder):
    """Handles the top-level running of the application"""

    def __init__(self, config: str = DEFAULT_CONFIG) -> None:
        self.config = config
        self.date = DEFAULT_DATE
        # TODO: Keep ledger as a string until you need to do more with it
        self.ledger = Ledger(DEFAULT_LEDGER)

    # TODO: Make a 'CSVFile' base class for ledger and config stuff?
    # e.g. `config = CSVFile(self.config_path).read()`
    def read_config(self) -> None:
        """Update application properties with values from the config file"""
        try:
            with open(self.config, 'r', newline='') as f:
                config = next(csv.DictReader(f))
        except FileNotFoundError:
            pass
        else:
            # TODO: Keep dates as strings until you need to do arithmetic
            self.date = datetime.date.fromisoformat(config['date'])
            self.ledger = Ledger(config['ledger'])

    def write_config(self) -> None:
        """Write key/value pairs to the config file"""
        with open(self.config, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'ledger'])
            writer.writeheader()
            writer.writerow(dict(date=self.date, ledger=self.ledger))

    # TODO: Get rid of all '_command' methods, prefer custom argparse actions?
    def _date_command(self, args: argparse.Namespace) -> None:
        if args.date is not None:
            # TODO: Just write the new date or ledger value straight to the config
            self.date = args.date
            self.write_config()
        elif args.days is not None:
            self.date += args.days
            self.write_config()
        else:
            print(self.date.isoformat())

    def _ledger_command(self, args: argparse.Namespace) -> None:
        if args.ledger is not None:
            self.ledger = args.ledger
            self.write_config()
        else:
            print(self.ledger.path)

    def _transaction_command(self, args: argparse.Namespace) -> None:
        if args.command == 'credit':
            args.amount *= -1
        self.ledger.append(
            id=len(self.ledger),
            date=self.date.isoformat(),
            amount='{:+.2f}'.format(args.amount),
            description=args.description,
        )

    # TODO: Get rid of '{:+.2f}' everywhere (use 'int' or subclass 'Decimal')
    def _report_command(self, args: argparse.Namespace) -> None:
        if args.command == 'balance':
            print('{:+.2f}'.format(self.ledger.balance(*args.datespec)))
        else:
            for row in self.ledger.tabulate(*args.datespec):
                print(row)

    def parse_args(self, argv: Union[Sequence[str], None] = None) -> argparse.Namespace:
        """Handles parsing, type-checking and casting of command line arguments"""
        parser = argparse.ArgumentParser(exit_on_error=False)
        subparsers = parser.add_subparsers(dest='command')

        date_parser = subparsers.add_parser(
            'date', exit_on_error=False, help='set a new application date'
        )
        date_parser.add_argument(
            'date',
            nargs='?',
            type=datetime.date.fromisoformat,
            metavar='<date>',
            help='a date in yyyy-mm-dd iso format',
        )
        date_parser.add_argument(
            '--advance',
            dest='days',
            type=daydelta,  # type: ignore [arg-type]
            nargs='?',
            const='1',
            metavar='<days>',
            help='the number of days to advance (default %(const)s day)',
        )
        date_parser.set_defaults(func=self._date_command)

        ledger_parser = subparsers.add_parser(
            'ledger', exit_on_error=False, help='select a new ledger file'
        )
        ledger_parser.add_argument(
            'ledger',
            type=Ledger,
            nargs='?',
            metavar='<ledger>',
            help='the path to the new ledger file',
        )
        ledger_parser.set_defaults(func=self._ledger_command)

        transaction_parser = subparsers.add_parser(
            'credit',
            aliases=['debit'],
            exit_on_error=False,
            help='credit the current ledger',
        )
        transaction_parser.add_argument(
            'amount',
            metavar='<amount>',
            type=Decimal,
            help='the amount to be credited',
        )
        transaction_parser.add_argument(
            '--description',
            '-d',
            metavar='<description>',
            help='a short description of the transation',
        )
        transaction_parser.set_defaults(func=self._transaction_command)

        report_parser = subparsers.add_parser(
            'report',
            aliases=['balance'],
            exit_on_error=False,
            help='display information about past transactions',
        )
        report_parser.add_argument(
            'datespec',
            nargs='?',
            action=DateSpecAction,
            default='~'.join([MIN_DATE.isoformat(), self.date.isoformat()]),
            metavar='<datespec>',
            help='A date or range of dates over which to report, of the form [YYYY-MM-DD~]YYYY-MM-DD',  # noqa: B950
        )
        report_parser.set_defaults(func=self._report_command)

        if not argv:
            argv = ['--help']
        return parser.parse_args(argv)

    # TODO: Add tests for BrokenPipeError and KeyboardInterrupt
    def run(self, argv: Union[Sequence[str], None] = None) -> int:
        """Run the program with the given arguments"""
        self.read_config()
        try:
            args = self.parse_args(argv)
            args.func(args)
        except argparse.ArgumentError as err:
            print(err, file=sys.stderr)
            return 1
        except (BrokenPipeError, KeyboardInterrupt):
            return 2
        else:
            return 0
