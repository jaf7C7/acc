'''Format, lint and test the entire project'''

import os
import subprocess


def clear():
    # Clear screen and scrollback: www.xfree86.org/current/ctlseqs.html
    print('\033c\033[3J')


def print_header(text=None):
    # '\033[1m' : start bold text
    # '\033[0m' : clear formatting
    columns, _ = os.get_terminal_size()
    print('\033[1m', f' {text} '.center(columns - 1, '='), '\033[0m', sep='')


def format():
    print_header('Black')
    subprocess.run('black --line-length 90 src/ tests/'.split())


def lint():
    print_header('Flake8')
    subprocess.run('flake8 src/ tests/'.split()).check_returncode()
    print('No errors to display :)')  # Only executes on success


def type_check():
    print_header('MyPy')
    subprocess.run('mypy src/'.split()).check_returncode()


# TODO: Allow passing extra args to pytest
def test():
    subprocess.run('pytest --cov=src/ tests/'.split())

def find_files(path):
    return [
        os.path.join(dirpath, file)
        for dirpath, _, filenames, in os.walk(path)
        for file in filenames
        if file.endswith('.py')
    ]

def generate_tags():
    print_header('Ctags')
    files = find_files('src/') + find_files('tests/')
    subprocess.run(['ctags', *files]).check_returncode()
    subprocess.run(['etags', *files]).check_returncode()
    print('tags updated')


def main():
    clear()
    format()
    lint()
    type_check()
    generate_tags()
    test()


if __name__ == '__main__':
    main()
