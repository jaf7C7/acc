Acc
===

> TODO:
> * Description
>   * This is a learning project
>   * What were the learning objectives?
> * Usage
> * Installation
> * Unix, Windows
> * Resurrect old python test script: `git checkout 2c5512d -- test.py`
>   and put both test scripts in `devutils` dir, avoiding `entr` and `ctags`
>   dependencies
> * Possible extensions/improvements
> * Similar projects (ledger-cli.org)


Acc is a command-line tool for managing a simple financial account. It is primarily
a learning project, and its functionality is not particularly interesting.


Usage
-----

Debits and credits can be recorded in a ledger of transactions, from which the
current balance can be calculated:

```
$ acc debit 78.47 --description 'Frobulant'
$ acc debit 25.55 -d 'Quxicator'
$ acc credit 101.99 -d 'Fremule'
$ acc report
ID      DATE        AMOUNT    TYPE    DESCRIPTION
0       1970-01-01  78.47     debit   Frobulant
1       1970-01-01  25.55     debit   Quxicator
2       1970-01-01  101.99    credit  Fremule
$ acc balance
2.03
```

Acc can report transactions from a specific date or range of dates:

```
$ acc ledger data/sample_ledger.csv
$ acc report 2018-10-10
ID      DATE        AMOUNT    TYPE    DESCRIPTION
59397   2018-10-10  3961.29   debit   Focus push find.
59398   2018-10-10  3520.57   credit  Tend soldier face prove.
59399   2018-10-10  1246.97   credit  Discussion create worker music worry.
[ ... ] # Output truncated
59434   2018-10-10  2558.06   credit  Help field center without loss.
59435   2018-10-10  394.45    debit   Nor general usually new effect assume.
59436   2018-10-10  847.18    debit   Health traditional certain me candidate start away.
$ acc report ~2018-10-10
acc report ~2018-10-10
```
