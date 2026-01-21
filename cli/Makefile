init:
	uv sync
	pnpm i

lint:
	uv run ruff check

lint-fix:
	uv run ruff check --fix

format: lint-fix
	uv run ruff format
	pnpm format

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +;
	rm -rf .ruff_cache