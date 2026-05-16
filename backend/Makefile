.DEFAULT_GOAL := run-app

PYTHON := python
PYTEST := $(PYTHON) -m pytest
DOCKER_COMPOSE := docker compose
APP_ENV ?= ../.env
TEST_ENV ?= ../.env.test
APP_COMPOSE := $(DOCKER_COMPOSE) -p curs-backend --env-file $(APP_ENV) -f docker-compose.yml
TEST_COMPOSE := $(DOCKER_COMPOSE) -p curs-backend-test --env-file $(TEST_ENV) -f docker-compose.test.yml

.PHONY: \
	run-app \
	update \
	seed \
	break \
	docker-build \
	docker-up \
	docker-down \
	docker-rebuild \
	docker-logs \
	test \
	test-unit \
	test-integration \
	test-api \
	test-cov \
	test-all \
	test-db-up \
	test-db-down \
	test-docker

docker-build:
	$(APP_COMPOSE) build migrate

run-app:
	$(PYTHON) -m uvicorn main:app

update:
	$(PYTHON) -m alembic upgrade head

seed:
	$(PYTHON) -m cli bootstrap load-seed

break:
	taskkill //F //IM python.exe //IM python3.exe //T

docker-up:
	$(APP_COMPOSE) up --build -d

docker-down:
	$(APP_COMPOSE) down

docker-rebuild:
	$(APP_COMPOSE) up --build -d

docker-logs:
	$(APP_COMPOSE) logs -f api

test:
	$(PYTEST)

test-unit:
	$(PYTEST) tests/unit

test-integration:
	$(PYTEST) tests/integration

test-api:
	$(PYTEST) tests/api

test-cov:
	$(PYTEST) --cov=. --cov-report=term-missing

test-all:
	$(PYTEST) tests/unit tests/integration tests/api

test-db-up:
	$(TEST_COMPOSE) up -d db redis --wait

test-db-down:
	$(TEST_COMPOSE) down -v

test-docker:
	$(TEST_COMPOSE) up --build --abort-on-container-exit --exit-code-from backend-test backend-test
