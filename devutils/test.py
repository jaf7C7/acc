'''Format, lint and test the entire project'''

import os
import sys
import subprocess


def help():
    print('Usage: python test.py [-c|--clear] [<pytest-options>]')


def clear():
    # Clear screen and scrollback: www.xfree86.org/current/ctlseqs.html
    print('\033c\033[3J')


def print_header(text=None):
    # '\033[1m' : start bold text
    # '\033[0m' : clear formatting
    columns, _ = os.get_terminal_size()
    print('\033[1m', f' {text} '.center(columns - 1, '='), '\033[0m', sep='')


def format():
    print_header('black')
    subprocess.run('black src/ tests/'.split()).check_returncode()


def lint():
    print_header('flake8')
    subprocess.run('flake8 src/ tests/'.split()).check_returncode()
    print('No errors to display :)')  # Only executes on success


def type_check():
    print_header('mypy')
    subprocess.run('mypy src/ tests/'.split()).check_returncode()


def test(argv):
    subprocess.run(['pytest', '--cov=src/', 'tests/', *argv])


def main(argv):
    if len(argv) > 0:
        if argv[0] in ['-h', '--help']:
            help()
            sys.exit()
        if argv[0] in ['-c', '--clear']:
            argv.pop(0)
            clear()
    format()
    lint()
    type_check()
    test(argv)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except subprocess.CalledProcessError:
        sys.exit(1)
