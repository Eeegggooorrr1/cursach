.DEFAULT_GOAL := dev

NPM ?= npm
DOCKER_COMPOSE := docker compose
APP_ENV ?= ../.env
TEST_ENV ?= ../.env.test
APP_COMPOSE := $(DOCKER_COMPOSE) -p curs-frontend --env-file $(APP_ENV) -f docker-compose.yml
TEST_COMPOSE := $(DOCKER_COMPOSE) -p curs-frontend-test --env-file $(TEST_ENV) -f docker-compose.test.yml

.PHONY: \
	install \
	dev \
	build \
	preview \
	docker-up \
	docker-down \
	docker-logs \
	test \
	test-docker

install:
	$(NPM) ci

dev:
	$(NPM) run dev

build:
	$(NPM) run build

preview:
	$(NPM) run preview

docker-up:
	$(APP_COMPOSE) up --build -d

docker-down:
	$(APP_COMPOSE) down

docker-logs:
	$(APP_COMPOSE) logs -f frontend

test:
	$(NPM) run test

test-docker:
	$(TEST_COMPOSE) up --build --abort-on-container-exit --exit-code-from frontend-test frontend-test
