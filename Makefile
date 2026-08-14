.PHONY: format lint typecheck test check sam-validate sam-local deploy delete ministack-health show-config

format:
	uv run ruff format

lint:
	uv run ruff check

typecheck:
	uv run ty check

test:
	uv run pytest tests

check: format lint typecheck test
