.PHONY: up down logs build test fmt lint migrate

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200 habit-bot

migrate:
	docker compose run --rm habit-bot alembic upgrade head

test:
	pytest -q

fmt:
	black .

lint:
	rufflehog . || true
