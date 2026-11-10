PYTHON      := uv run python
FLAKE8      := uv run flake8
MYPY        := uv run mypy
TEST        := uv run pytest
MAIN        := src
EXCLUDE     := .venv,llm_sdk

MYPY_FLAGS  := --warn-return-any --warn-unused-ignores --ignore-missing-imports \
               --disallow-untyped-defs --check-untyped-defs

ARGS        ?=

.PHONY: all install run debug test clean lint lint-strict

all: install

install:
	uv sync

run:
	$(PYTHON) -m $(MAIN) $(ARGS)

debug:
	$(PYTHON) -m pdb -m $(MAIN) $(ARGS)

test:
	$(TEST)

clean:
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	$(FLAKE8) . --exclude $(EXCLUDE)
	$(MYPY) . $(MYPY_FLAGS) --exclude '^(\.venv|llm_sdk)/'

lint-strict:
	$(FLAKE8) . --exclude $(EXCLUDE)
	$(MYPY) . --strict --exclude '^(\.venv|llm_sdk)/'
