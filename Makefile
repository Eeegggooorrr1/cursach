.DEFAULT_GOAL := run-app

PYTHON := python
PYTEST := $(PYTHON) -m pytest
DOCKER_COMPOSE := docker compose
TEST_DOCKER_COMPOSE := $(DOCKER_COMPOSE) -p curs-test --env-file .env.test -f docker-compose.test.yml

.PHONY: \
	run-app \
	update \
	seed \
	break \
	up \
	stop \
	down \
	rebuild \
	test \
	test-unit \
	test-db-up \
	test-db-down \
	test-integration \
	test-api \
	test-cov \
	test-all

run-app:
	uvicorn main:app

update:
	alembic upgrade head

seed:
	$(PYTHON) -m cli bootstrap load-seed

break:
	taskkill //F //IM python.exe //IM python3.exe //T

up:
	$(DOCKER_COMPOSE) up

stop:
	$(DOCKER_COMPOSE) stop

down:
	$(DOCKER_COMPOSE) down

rebuild:
	$(DOCKER_COMPOSE) up --build

test:
	$(PYTEST)

test-unit:
	$(PYTEST) tests/unit

test-db-up:
	$(TEST_DOCKER_COMPOSE) up -d --wait

test-db-down:
	$(TEST_DOCKER_COMPOSE) down -v

test-integration:
	$(PYTEST) tests/integration

test-api:
	$(PYTEST) tests/api

test-cov:
	$(PYTEST) --cov=. --cov-report=term-missing

test-all:
	$(PYTEST) tests/unit tests/integration tests/api
