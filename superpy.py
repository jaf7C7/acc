import datetime


def get_date():
    try:
        with open(".superpy.conf", "r") as date_file:
            date = date_file.read()
    except FileNotFoundError:
        date = "1970-01-01"
    return date


def write_date(date):
    with open(".superpy.conf", "w") as date_file:
        date_file.write(date)


def main(argv=None):
    if argv is None:
        return 1
    if len(argv) > 1:
        if argv[1] == "--advance":
            days = int(argv[2]) if len(argv) == 3 else 1
            date = datetime.date.fromisoformat(get_date())
            date += datetime.timedelta(days=days)
            write_date(date.isoformat())
        else:
            write_date(argv[1])
    elif argv[0] == "date":
        date = get_date()
        print(date)
    elif argv[0] == "ledger":
        print("superpy_ledger.csv")
    return 0
