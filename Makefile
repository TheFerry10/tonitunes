sources = src tests app examples
test_dir = tests
virtual_env = venv
SHELL := /bin/bash
python := ./$(virtual_env)/bin/python
pytest := ./$(virtual_env)/bin/pytest

.PHONY: exists
exists:
	if [ -d ./$(virtual_env) ]; then \
		echo "Dir exists"; \
	else \
		echo "Dir not exists"; \
	fi

.PHONY: install
install:
	python -m venv $(virtual_env) && \
	source ./venv/bin/activate && \
	pip install -r requirements.txt

.PHONY: format
format:
	black $(sources)

.PHONY: lint
lint:
	black $(sources) --check --diff
	@echo "======="
	flake8 $(sources)

.PHONY: isort
isort:
	isort $(sources)

.PHONY: test
test:
	$(pytest) $(test_dir)

.PHONY: inspect-coverage
inspect-coverage:
	xdg-open htmlcov/index.html

.PHONY: clean
clean:
	rm -rf $(virtual_env)
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
