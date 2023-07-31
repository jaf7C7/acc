def get_date():
    try:
        with open("superpy_date", "r") as date_file:
            date = date_file.read()
    except FileNotFoundError:
        date = "1970-01-01"
    return date


def main(argv=None):
    if argv is None:
        return 1
    if len(argv) > 1:
        if argv[1] == "--advance":
            date = get_date()
            day = int(date[-2:])
            day += 1
            new_date = f"{date[:-2]}{day:02}"
            with open("superpy_date", "w") as date_file:
                date_file.write(new_date)
        else:
            with open("superpy_date", "w") as date_file:
                date_file.write(argv[1])
    elif argv[0] == "date":
        date = get_date()
        print(date)
    return 0
