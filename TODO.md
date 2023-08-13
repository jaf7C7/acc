# TODO

- [x] Does the application return 1 if no args are passed?
- [x] Does `date` return `1970-01-01\n` to stdout?
- [x] Does `date` return 0 args are not `None`?
- [x] Can the application set and get the date?
- [x] Does `date --advance N` advance the date by `N` days??
- [x] Does `date --advance` default to 1 day?
- [x] Does `ledger` return `superpy_ledger.csv`
- [x] Can the application set and get the ledger path?
- [x] Rewrite argument parsing using `argparse`
- [x] `date <date>` fails if `<date>` is not YYYY-MM-DD ISO format
- [x] `date --advance <days>` fails if `<days>` is not an integer
- [x] Can the application remember and recall a sequence of simple transactions?
- [x] Refactoring!
- [x] Do `set_date` and `set_ledger` reset each other?
- [x] Get test coverage up to 100%
- [x] Does `report` fail if there`s no ledger file?
- [x] Refactoring
- [x] CSV file formats
- [x] Output formatting
- [x] Clean up git history
- [x] OOP-ify
- [x] Tests should invoke a separate application instance for each command
- [x] Add `__repr__` to classes
- [X] Helpful error messages
- [x] Decide a ledger format which can record purchases and sales
- [x] Can the user sell items as well as buying them?
- [x] Report profit
- [x] Redesign ledger format (need to use double-entry bookkeeping)
- [x] Refactor report methods
- [x] Ledger, Transaction and Product objects to simplify business logic
- [x] Remove unnecessary dependencies on datetime and Ledger from Config
- [x] from datetime import date as Date daydelta => DayDelta
- [x] Get rid of @property date and ledger (and setters), and _date and _ledger, just do: self.date = args.date, self.config.write(self.__dict__.values())
- [x] simplify __repr__() on all?
- [x] Transaction should be a short-lived dict internal to Ledger and NOT a class
- [x] DictReader : fieldnames optional (read from first line of file, so write a header)
- [x] Ledger.__iter__() should yield from csv.DictReader(f, fieldnames=self.fieldnames)
- [ ] Add doc strings
- [ ] Add type hints
- [ ] Dependency injection (see <https://www.youtube.com/watch?v=lX9UQp2NwTk&t=858s>)
- [ ] Report income
- [ ] Report expenses
- [ ] Report over a range of dates
- [ ] JSON file formats


ledger format: <https://www.wikihow.com/Write-an-Accounting-Ledger>

> NOTE: *credit* => money going out, *debit* => money going in

superpy_ledger.csv
```
date,product,units,debit,credit,balance
```


superpy TODO

12 August 2023
04:31
