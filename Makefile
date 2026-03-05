.PHONY: build up dev down logs seed test shell-api clean

build:
	docker compose build

up:
	docker compose up -d

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec api python -m api.seed

test:
	docker compose exec api python -m pytest tests/ -v

shell-api:
	docker compose exec api bash

clean:
	docker compose down -v --rmi local --remove-orphans
