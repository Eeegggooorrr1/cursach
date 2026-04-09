.DEFAULT_GOAL := run

run:
	uvicorn main:app

migrate:
	alembic revision --autogenerate -m 'hi'

update:
	alembic upgrade head

.PHONY: seed
seed:
	python -m cli bootstrap load-seed

break:
	taskkill //F //IM python.exe //IM python3.exe //T



up:
	docker compose up

stop:
	docker compose stop

down:
	docker compose down

rebuild:
	docker compose up --build