.PHONY: docs
init:
	pip install pipenv
	pipenv install --dev --skip-lock

docs:
	cd docs && make html

test:
	pipenv run python -m unittest
