import sys
import datetime
import argparse
import csv


def cli(argv):
    app = Application()
    return app.run(argv)


class DayDelta(datetime.timedelta):
    def __new__(cls, days):
        return super().__new__(cls, days=int(days))


class Config:
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f"{self.__class__.__name__}(path={self.path})"

    def read(self):
        try:
            with open(self.path, "r", newline="") as f:
                return next(csv.reader(f))
        except FileNotFoundError:
            return "1970-01-01", "superpy_ledger.csv"

    def write(self, attrs):
        with open(self.path, "w", newline="") as f:
            csv.writer(f).writerow(attrs)


class Transaction:
    def __init__(self, date, product, units=1, debit=0, credit=0, balance=0):
        self.date = date
        self.product = product
        self.units = int(units)
        self.debit = int(debit)
        self.credit = int(credit)
        self.balance = int(balance)

    def __str__(self):
        return f"{self.date:12}{self.product:12}{self.debit:6}{self.credit:6}{self.balance:6}"  # noqa: E501

    def __repr__(self):
        attrs = ", ".join(f"{k}='{v}'" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


class Ledger:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path

    def __repr__(self):
        attrs = ", ".join(f"{k}='{v}'" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    def __eq__(self, other):
        return self.path == other.path

    def __iter__(self):
        try:
            with open(self.path, "r", newline="") as f:
                yield from map(lambda t: Transaction(*t), csv.reader(f))
        except FileNotFoundError:
            pass

    def append(self, transaction):
        with open(self.path, "a", newline="") as f:
            csv.writer(f).writerow(vars(transaction).values())

    def profit(self):
        try:
            return sum(map(lambda t: t.balance, self))
        except FileNotFoundError:
            return 0


class Application:
    def __init__(self, config_path=".superpy.conf"):
        self.config = Config(config_path)
        date_string, ledger_path = self.config.read()
        self._date = datetime.date.fromisoformat(date_string)
        self._ledger = Ledger(ledger_path)

    def __repr__(self):
        attrs = ", ".join(f"{k.lstrip('_')}='{v}'" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = date
        self.config.write((self._date, self._ledger))

    @property
    def ledger(self):
        return self._ledger

    @ledger.setter
    def ledger(self, ledger):
        self._ledger = ledger
        self.config.write((self._date, self._ledger))

    @staticmethod
    def parse_args(argv):
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
            "--profit",
            action="store_const",
            const="profit",
            dest="report_type",
            help="see how much profit has been made",
        )

        return parser.parse_args(argv)

    def run(self, argv=None):
        try:
            args = self.parse_args(argv)
        except argparse.ArgumentError as err:
            print(err, file=sys.stderr)
            return 1

        if args.command == "date":
            if args.date is not None:
                self.date = args.date
            elif args.days is not None:
                self.date += args.days
            else:
                print(self.date)

        elif args.command == "ledger":
            if args.ledger is not None:
                self.ledger = args.ledger
            else:
                print(self.ledger)

        elif args.command in {"buy", "sell"}:
            debit = args.price * args.units if args.command == "sell" else 0
            credit = args.price * args.units if args.command == "buy" else 0
            transaction = Transaction(
                date=self.date,
                product=args.product,
                units=args.units,
                debit=debit,
                credit=credit,
                balance=(debit - credit),
            )
            self.ledger.append(transaction)

        elif args.command == "report":
            if args.report_type == "profit":
                print(self.ledger.profit())
            else:
                for transaction in self.ledger:
                    print(transaction)
        return 0
