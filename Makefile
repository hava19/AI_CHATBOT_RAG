.PHONY: help install dev test run migrate docker-up

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  migrate     Run database migrations"
	@echo "  docker-up   Start Docker services"

install:
	pip install -r requirements/dev.txt

dev:
	uvicorn app.main:app --reload

test:
	pytest tests/ -v

migrate:
	alembic upgrade head

docker-up:
	docker-compose up -d
