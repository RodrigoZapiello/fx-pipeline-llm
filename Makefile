.PHONY: build run shell test dashboard

build:
	docker compose build

run:
	docker compose run --rm app

shell:
	docker compose run --rm app bash

dashboard:
	docker compose up dashboard

test:
	pytest -q
