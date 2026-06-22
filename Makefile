.PHONY: install test lint build smoke clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m unittest discover -s tests

lint:
	ruff check .

build:
	python -m build

smoke:
	shardflow --version
	shardflow schema --format markdown
	shardflow index examples/data --output /tmp/shardflow-manifest.json
	shardflow inspect --manifest /tmp/shardflow-manifest.json --format markdown
	shardflow verify --manifest /tmp/shardflow-manifest.json

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache
