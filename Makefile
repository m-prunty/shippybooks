install:
	uv sync

install-prod:
	uv sync --frozen --no-dev

run:
	uv run uvicorn shippybooks.main:app --reload

test:
	uv run pytest

lint:
	uv run mypy --strict src
