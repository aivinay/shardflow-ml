PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_RUFF := $(VENV)/bin/ruff

.PHONY: install test lint build smoke check docker clean

install:
	$(PYTHON) -m venv --clear $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -e ".[dev]"

test:
	PYTHONPATH=src $(VENV_PYTHON) -m unittest discover -s tests

lint:
	$(VENV_RUFF) check .

build:
	$(VENV_PYTHON) -m build

smoke:
	PYTHONPATH=src $(VENV_PYTHON) -m shardflow.cli --version
	PYTHONPATH=src $(VENV_PYTHON) -m shardflow.cli doctor --data-dir examples/data
	PYTHONPATH=src $(VENV_PYTHON) -m shardflow.cli schema --format markdown
	PYTHONPATH=src $(VENV_PYTHON) -m shardflow.cli index examples/data --output /tmp/shardflow-manifest.json
	PYTHONPATH=src $(VENV_PYTHON) -m shardflow.cli inspect --manifest /tmp/shardflow-manifest.json --format markdown
	PYTHONPATH=src $(VENV_PYTHON) -m shardflow.cli verify --manifest /tmp/shardflow-manifest.json

check: lint test build smoke

docker:
	docker build -t shardflow-ml:dev .

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
