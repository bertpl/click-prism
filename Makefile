.PHONY: help dev-setup build test coverage format lint update-deps release docs show-coverage show-docs

help:
	@echo 'Commands:'
	@echo '  dev-setup   One-time: sync dev deps + install pre-commit hooks'
	@echo '  build       Build package'
	@echo '  test        Run pytest'
	@echo '  coverage    Multi-run coverage report (./reports/coverage)'
	@echo '  format      Format and fix with ruff'
	@echo '  lint        Ruff check'
	@echo '  update-deps Re-resolve uv.lock to latest versions'
	@echo '  release     Bump version, validate, tag, push'
	@echo '  docs        Build mkdocs site (./reports/docs)'

dev-setup:
	uv sync --group dev
	uv run pre-commit install

build:
	uv build

test:
	uv run pytest ./tests --durations=20

coverage:
	mkdir -p ./reports
	# 1. Without Rich — covers fallback paths
	uv sync --group dev
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --durations=20
	# 2. With Rich — covers Rich renderer
	uv sync --group dev --extra rich
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --cov-append --durations=20
	# 3. With Rich + rich-click — covers style inheritance
	uv pip install rich-click
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --cov-append --durations=20
	# 4. + ecosystem compat — covers any code paths gated on
	#    cloup / click-extra / click-didyoumean / click-help-colors /
	#    click-default-group / click-aliases being present
	uv pip install cloup click-extra click-didyoumean \
		click-help-colors click-default-group click-aliases
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --cov-append --durations=20
	# Report
	COVERAGE_FILE=./reports/.coverage \
		uv run coverage report --fail-under=100
	COVERAGE_FILE=./reports/.coverage \
		uv run coverage html -d ./reports/coverage
	# Restore base dev environment
	uv sync --group dev

format:
	uv run ruff format click_prism tests
	uv run ruff check --fix click_prism tests

lint:
	uv run ruff check click_prism tests

update-deps:
	uv lock --upgrade

release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=X.Y.Z" && exit 1)
	$(MAKE) coverage
	uv run python scripts/release.py $(VERSION)

docs:
	uv sync --group docs
	uv run mkdocs build

show-coverage:
	open ./reports/coverage/index.html

show-docs:
	open ./reports/docs/index.html
