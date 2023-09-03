test:
	. .venv/bin/activate \
	&& find src/ tests/ -name \*.py | entr python test.py
