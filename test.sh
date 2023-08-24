# Format, lint and test the entire project
find . -name acc.py -o -name test_acc.py | entr -cs '
	print_header () {
		: "${COLUMNS:=79}"
		set -- " $* "
		while test ${#1} -lt $((COLUMNS - 1))
		do
			set -- "=${1}="
		done
		test ${#1} -lt $COLUMNS && set -- "${1}="
		printf "\033[1m%s\033[0m\n" "$1"  # Bold
	}

	set -e
	. .venv/bin/activate

	test -n "$TMUX_PANE" && tmux clear -t "$TMUX_PANE"

	print_header "Black"
	black --line-length 90 "$0"

	print_header "Flake8"
	flake8 "$0" && echo "No errors to display :)"

    print_header "MyPy"
    mypy "$0"

	pytest --cov=. '"$*"'
'
