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
