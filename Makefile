.PHONY: setup format format-check lint typecheck imports test test-unit test-integration check

setup:
	uv sync
	uv pip install -e .

format:
	uv run ruff format

format-check:
	uv run ruff format --check

lint:
	uv run ruff check

typecheck:
	uv run ty check

imports:
	uv run lint-imports

test:
	uv run pytest tests

test-unit:
	uv run pytest tests/unit

test-integration:
	uv run pytest tests/integration

check: format-check lint typecheck imports test
