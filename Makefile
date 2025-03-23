.PHONY: format lint dev-lint

GIT_ROOT ?= $(shell git rev-parse --show-toplevel)

dev-lint:
	black .
	mypy .
	ruff check . --fix
	isort .
	pylint ai_rpg/. --max-line-length 120 --disable=R,C,I  --fail-under=9

lint:
	black . --check
	mypy .
	ruff check .
	isort . --check-only
	pylint ai_rpg/. --max-line-length 120 --disable=R,C,I,W1203,W0107 --fail-under=9