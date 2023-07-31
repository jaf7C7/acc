def main(argv=None):
    if argv is None:
        return 1
    if len(argv) > 1:
        with open("superpy_date", "w") as date_file:
            date_file.write(argv[1])
    elif argv[0] == "date":
        try:
            with open("superpy_date", "r") as date_file:
                date = date_file.read()
        except FileNotFoundError:
            date = "1970-01-01"
        print(date)
    return 0
