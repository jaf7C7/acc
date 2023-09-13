#!/bin/sh
#
# Watch all python files in `src/` and `tests/` directories, and run
# the script if files change

CTAGS=$(command -v uctags || command -v ctags); export CTAGS

find src/ tests/ -name \*.py | entr -ccs '

    # `==== <text> ====`
    print_header () {
        : "${COLUMNS:=79}"
        set -- " $* "
        while test ${#1} -lt $((COLUMNS - 1)); do
            set -- "=${1}="
        done
        test ${#1} -lt $COLUMNS && set -- "${1}="
        printf "\033[1m%s\033[0m\n" "$1"  # Bold
    }

    # Stop on first error
    set -e

    # Clear tmux scrollback
    test -n "$TMUX_PANE" && tmux clear -t "$TMUX_PANE"

    # Set up virtual environment
    . .venv/bin/activate

    # Generate tags for all files
    find src/ tests/ -name \*.py -exec "$CTAGS" "$@" {} +

    # Format
    print_header "black"
    black --line-length 90 src/ tests/

    # Lint
    print_header "flake8"
    flake8 src/ tests/
    echo "No errors to display :)"

    # Type-check
    print_header "mypy"
    mypy src/

    # Run all tests (any command-line options will be passed to pytest)
    pytest --cov=src/ tests/ '"$*"'

'
