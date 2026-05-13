manage = python3 manage.py

.PHONY: install migrate run check makemigrations test docker-up
install:
	python3 -m pip install -r requirements.txt

makemigrations:
	$(manage) makemigrations

migrate:
	$(manage) migrate

run:
	$(manage) runserver 0.0.0.0:8000

check:
	$(manage) check

test:
	$(manage) test

docker-up:
	docker compose up --build
