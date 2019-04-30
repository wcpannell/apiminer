.PHONY: docs
init:
	pip install poetry

docs:
	cd docs && poetry run make html

test:
	tox
