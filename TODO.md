# TODO

- [ ] Ledger.append type hint remove int
- [ ] Split Application run into smaller methods. (and alias debit to credit as they do exact same thing)
- [ ] Type hint parse_args -> Union[namespace, None] as it can print help (same for cli.main)
- [ ] Type hint Ledger.balance -> Decimal not int
- [ ] Report should report up until current date
- [ ] Ledger should have a print method, _collimate, _tabulate
- [ ] Reduce duplication of `CONFIG_PATH`/`LEDGER_PATH` in tests
- [ ] Add two more types of reporting
- [ ] Report over a range of dates
- [ ] Streamline cli a bit (e.g. `acc balance` vs. `acc report --balance`)
- [ ] Add documentation
- [ ] Add README.md
- [ ] Next project!

