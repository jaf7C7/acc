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
- [ ] Ledger, Transaction and Product objects to simplify business logic
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
