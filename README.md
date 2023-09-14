Acc
===

A command-line tool for managing a simple financial account. It is primarily a
learning project, and its functionality is not particularly interesting, although
it is described briefly in the [Usage](#usage) section.

For a much more complete command-line accounting tool, see
[ledger-cli](https://ledger-cli.org)

The main goals of this project were:

* To gain experience with using and understanding python standard library modules
* To learn about object-oriented programming and design
* To practice a test-driven development workflow
* To get familiar with the process of writing a command-line tool in python


Installation
------------

On Linux/macOS/FreeBSD:

Clone and enter the repo:
```
$ git clone https://github.com/jaf7C7/acc && cd acc
```

Initialise a virtual environment:
```
$ python -m venv .venv && . .venv/bin/activate
```

Install the package locally:
```
$ pip install -e . && ln -s $PWD/bin/acc $VIRTUAL_ENV/bin
```

Run the tests (optional):
```
$ pip install -r dev_requirements.txt && python devutils/test.py
```

On Windows:

> TODO


Usage
-----

Debits and credits can be recorded in a ledger of transactions, from which the
current balance can be calculated:

Check the ledger file:
```
$ acc ledger
acc_ledger.csv
```

Select a new ledger file:
```
$ acc ledger my_ledger.csv
```

Check the date:
```
$ acc date
1970-01-01
```

Change the date:
```
$ acc date 2023-09-13
```

Add some transactions:
```
$ acc debit 78.47 --description 'Frobulant'
$ acc debit 25.55 -d 'Quxicator'
$ acc credit 101.99 -d 'Fremule'
```

Print a handy table of your account history:
```
$ acc report
ID      DATE          AMOUNT  DESCRIPTION
0       2023-09-13    +78.47  Frobulant
1       2023-09-13    +25.55  Quxicator
2       2023-09-13   -101.99  Fremule
```

Check the overall balance on your account:
```
$ acc balance
+2.03
```

`acc` can report transactions from a specific date or range of dates:

Use the sample data file included in this project:
```
$ acc ledger data/sample_ledger.csv
```

List all transactions for the given date:
```
$ acc report 2018-10-10
ID      DATE          AMOUNT  DESCRIPTION
59397   2018-10-10  +3961.29  Focus push find.
59398   2018-10-10  -3520.57  Tend soldier face prove.
[ ... ] # Output truncated
59435   2018-10-10   +394.45  Nor general usually new effect assume.
59436   2018-10-10   +847.18  Health traditional certain me candidate start away.
```

The default is to report all transactions up until the current date:
```
$ acc date 2019-01-01
$ acc report
ID      DATE          AMOUNT  DESCRIPTION
0       2018-03-27  -7617.10  Mrs itself off treatment daughter author field.
1       2018-03-27  +5648.38  Base voice style democratic although apply morning later.
2       2018-03-27  +4041.84  Word personal attention.
3       2018-03-27  +3687.01  School other positive.
[ ... ]
10266   2019-01-01  +5343.10  Charge property minute away fight.
10267   2019-01-01  -8205.88  Fine community play try forward by take.
10268   2019-01-01  -2606.86  Usually concern nothing always pick animal body.
```

To specify other ranges use two dates separated by `~`:
```
$ acc report 2018-03-01~2018-04-01
ID      DATE          AMOUNT  DESCRIPTION
0       2018-03-27  -7617.10  Mrs itself off treatment daughter author field.
1       2018-03-27  +5648.38  Base voice style democratic although apply morning later.
[ ... ]
229     2018-04-01  -7517.27  Bag part prove conference spring discover management.
230     2018-04-01  -8720.78  Just identify responsibility could attack guess do.
231     2018-04-01  -2163.18  Charge tend hope.
```

Either date can be omitted to see all transactions preceding or following a certain
date:
```
$ acc report 2022-02-02~
ID      DATE          AMOUNT  DESCRIPTION
51313   2022-02-02  +1493.21  May television care.
51314   2022-02-02  -1170.45  Worker south worry other hear nice fish.
[ ... ]
66666   2023-03-27  -1420.60  Let manager live into.
66667   2023-03-27  -6547.91  Law news rate fear inside policy.
66668   2023-03-27  +2150.10  Natural seek race night need relate.
```

To calculate the balance over that same period, use the `balance` command:
```
$ acc balance 2022-02-02~
-932873.03  # Ouch!
```

To get the balance of the entire ledger, regardless of whatever the current date is
set to, omit both dates and just use `~`, making sure to quote it to avoid expansion
by your shell:
```
$ acc balance \~
-447127.92
```
