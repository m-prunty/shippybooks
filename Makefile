install:
	uv sync

install-prod:
	uv sync --frozen --no-dev

run:
	uv run uvicorn shippybooks.main:app --reload

test:
	uv run pytest

type:
	uv run mypy src
