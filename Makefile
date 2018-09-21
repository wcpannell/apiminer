.PHONY: docs
init:
	pip install pipenv
	pipenv install --dev --skip-lock

docs:
	cd docs && make html

citest:
	pipenv run pytest

test:
	detox