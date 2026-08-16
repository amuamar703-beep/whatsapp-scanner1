.PHONY: help install dev install-prod migrate upgrade downgrade run run-worker run-all test lint format clean docker-build docker-up docker-down docker-logs

help:
	@echo "Available commands:"
	@echo "  install         Install development dependencies"
	@echo "  install-prod    Install production dependencies"
	@echo "  migrate         Run database migrations"
	@echo "  upgrade         Upgrade database to latest migration"
	@echo "  downgrade       Downgrade database migration"
	@echo "  run             Run the bot"
	@echo "  run-worker      Run the worker"
	@echo "  run-all         Run both bot and worker"
	@echo "  test            Run tests"
	@echo "  lint            Run linting"
	@echo "  format          Format code"
	@echo "  clean           Clean temporary files"
	@echo "  docker-build    Build Docker images"
	@echo "  docker-up       Start Docker containers"
	@echo "  docker-down     Stop Docker containers"
	@echo "  docker-logs     View Docker logs"

install:
	pip install -r requirements-dev.txt
	pip install -r requirements.txt
	pre-commit install

install-prod:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

run:
	python -m app.main

run-worker:
	python -m app.worker_main

run-all:
	make run & make run-worker

test:
	pytest -v --cov=app --cov-report=term-missing

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

lint:
	flake8 app
	mypy app

format:
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf logs/*.log

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	rm -rf logs/*
	rm -rf storage/exports/*