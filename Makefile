NAME = shippybooks
RUN = uv run
MAIN = shippybooks.main:app
SRC = src/shippybooks

DIR_DIAG = diagrams
DIR_CLEAN = .mypy_cache .pytest_cache __pycache__ $(DIR_DIAG)
DIR_FCLEAN = .venv
FILE_CLEAN = '*.pyc' '*.pyo' '.*sw*'


install:
	uv sync

install-prod:
	uv sync --frozen --no-dev

run:
	$(RUN) uvicorn $(MAIN) --reload

test:
	$(RUN) pytest

lint:
	$(RUN) mypy --strict src

diagrams: | _diagrams_dir 
	$(RUN) pyreverse $(SRC) -o mmd
	$(RUN) pyreverse $(SRC) -o png 
	mv classes.mmd $(DIR_DIAG)/classes.mmd
	mv packages.mmd $(DIR_DIAG)/project.mmd
	mv classes.png $(DIR_DIAG)/classes.png
	mv packages.png $(DIR_DIAG)/project.png
	$(RUN) python scripts/gen_control_flow.py

readme: diagrams
	$(RUN) python scripts/gen_readme.py

_diagrams_dir:
	mkdir -p $(DIR_DIAG)

clean:
	find . -type d \( $(foreach d,$(DIR_CLEAN),-name $(d) -o) -false \) -prune -exec rm -rf {} +
	find . -type f \( $(foreach f,$(FILE_CLEAN),-name $(f) -o) -false \) -delete

fclean: clean
	find . -type d \( $(foreach d,$(DIR_FCLEAN),-name $(d) -o) -false \) -prune -exec rm -rf {} +

.PHONY: install install-prod run test lint diagrams readme _diagrams_dir clean
