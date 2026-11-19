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

diagrams: | _diagrams_dir
	cd diagrams && uv run pyreverse ../src/shippybooks -o png -p shippybooks && mv classes_shippybooks.png classes.png && mv packages_shippybooks.png project.png
	dot -Tpng diagrams/control-flow.dot -o diagrams/control-flow.png

_diagrams_dir:
	mkdir -p diagrams

clean:
	find . -type d \( -name '.mypy_cache' -o -name '.pytest_cache' \
		-o -name '__pycache__' \) -prune -exec rm -rf {} +
	find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
	find . -type f \( -name '.*.sw*' \) -delete

fclean: clean
	find . -type d -name '.venv' -prune -exec rm -rf {} +

.PHONY: install install-prod run test lint diagrams _diagrams_dir clean
