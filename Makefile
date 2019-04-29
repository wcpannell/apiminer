.PHONY: docs
init:
	pip install poetry

docs:
	poetry install
	cd docs && make html

test:
	tox
