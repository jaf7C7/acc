import sys
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

    def __repr__(self):
        attrs = ", ".join(f"{k.lstrip('_')}='{v}'" for k, v in self.__dict__.items())
        return f"Application({attrs})"

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
    def date(self, date):
        self._date = date
        self.write_config()

    @property
    def ledger(self):
        return self._ledger

    @ledger.setter
    def ledger(self, ledger):
        self._ledger = ledger
        self.write_config()

    def write_transaction_to_ledger(self, type, product, price, units):
        with open("superpy_ledger.csv", "a") as ledger:
            csv.writer(ledger).writerow([self.date, type, product, price, units])

    def report(self):
        with open(self.ledger, "r") as ledger:
            print("DATE        TYPE      PRODUCT     PRICE   UNITS   TOTAL")
            for date, type, product, price, units in csv.reader(ledger):
                price, units = int(price), int(units)
                total = price * units if type == "Sale" else -price * units
                print(
                    f"{date:10}  {type:8}  {product:10}  {price:<6}  {units:<6}  {total:<+}"  # noqa: E501
                )

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
            type=daydelta,
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

        report_parser = subparsers.add_parser(  # noqa: F841
            "report",
            exit_on_error=False,
            help="display information about past transactions",
        )

        return parser.parse_args(argv)

    def run(self, argv=None):
        self.read_config()
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

        elif args.command == "buy":
            self.write_transaction_to_ledger(
                "Purchase", args.product, args.price, args.units
            )

        elif args.command == "sell":
            self.write_transaction_to_ledger(
                "Sale", args.product, args.price, args.units
            )

        elif args.command == "report":
            try:
                self.report()
            except FileNotFoundError:
                return 1

        return 0
