.PHONY: setup format lint typecheck test check

setup:
	uv sync
	uv pip install -e .

format:
	uv run ruff format

lint:
	uv run ruff check

typecheck:
	uv run ty check

test:
	uv run pytest tests

check: format lint typecheck test
