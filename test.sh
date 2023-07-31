# Format, lint and test the entire project
find . -name \*.py | entr -cs '
	test -n "$TMUX_PANE" && tmux clear -t "$TMUX_PANE"
	print_header () {
		: "${COLUMNS:=79}"
		set -- " $* "
		while test ${#1} -lt $((COLUMNS - 1))
		do
			set -- "=${1}="
		done
		test ${#1} -lt $COLUMNS && set -- "${1}="
		printf "\\e[1m%s\\e[0m\\n" "$1"  # Bold
	}

	set -e
	. venv/bin/activate

	print_header "Black"
	black "$0"

	print_header "Flake8"
	flake8 "$0" && echo "No errors to display :)"

	pytest --cov=. '"$*"'
'
