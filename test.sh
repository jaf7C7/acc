# Format, lint and test the entire project
find . -name \*superpy.py | entr -cs '
	. venv/bin/activate
	test -n "$TMUX_PANE" && tmux clear -t "$TMUX_PANE"
	pytest --cov=. '"$*"'
'
