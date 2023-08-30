# Format, lint and test the entire project
find src/ tests/ -name \*.py | entr -s '
    print_header () {
        : "${COLUMNS:=79}"
        set -- " $* "
        while test ${#1} -lt $((COLUMNS - 1)); do
            set -- "=${1}="
        done
        test ${#1} -lt $COLUMNS && set -- "${1}="
        printf "\033[1m%s\033[0m\n" "$1"  # Bold
    }

    set -e
    . .venv/bin/activate

    clear             # Does not clear scrollback on freebsd
	printf "\033[3J"  # xterm erase saved lines (www.xfree86.org/current/ctlseqs.html)
    test -n "$TMUX_PANE" && tmux clear -t "$TMUX_PANE"

    find src/ tests/ -name \*.py -exec sh -c '\''ctags "$@"; etags "$@";'\'' {} +

    print_header "Black"
    black --line-length 90 src/ tests/

    print_header "Flake8"
    flake8 src/ tests/ && echo "No errors to display :)"

    print_header "MyPy"
    mypy src/

    pytest --cov=src/ tests/ '"$*"'
'
