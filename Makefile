.DEFAULT_GOAL := up

-include .env

COMPOSE := docker compose
APP_COMPOSE := $(COMPOSE) -f docker-compose.yml
TEST_ENV ?= .env.test
TEST_COMPOSE := $(COMPOSE) -p curs-test --env-file $(TEST_ENV) -f docker-compose.test.yml
FRONTEND_URL := http://localhost:$(FRONTEND_PORT)
BACKEND_URL := http://localhost:$(BACKEND_PORT)

.PHONY: \
	build \
	build-backend \
	up \
	down \
	restart \
	logs \
	print-info \
	migrate \
	seed \
	init \
	test \
	test-backend \
	test-frontend \
	test-down \
	clean

build-backend:
	$(APP_COMPOSE) build backend-migrate

build:
	$(APP_COMPOSE) build

up:
	$(APP_COMPOSE) up --build -d
	$(MAKE) --no-print-directory print-info

down:
	$(APP_COMPOSE) down

restart: down up

logs:
	$(APP_COMPOSE) logs -f

print-info:
	@printf "\n"
	@printf "Project is running:\n"
	@printf "  Frontend: $(FRONTEND_URL)\n"
	@printf "  Backend:  $(BACKEND_URL)\n"
	@printf "\n"
	@printf "Logs:\n"
	@printf "  make logs\n"
	@printf "\n"

migrate:
	$(APP_COMPOSE) up -d db
	$(APP_COMPOSE) run --build --rm backend-migrate

seed: build-backend
	$(APP_COMPOSE) up -d db
	$(APP_COMPOSE) run --rm --no-deps backend-seed

init: migrate seed

test: test-backend test-frontend

test-backend:
	$(TEST_COMPOSE) up --build --abort-on-container-exit --exit-code-from backend-test backend-test

test-frontend:
	$(TEST_COMPOSE) up --build --abort-on-container-exit --exit-code-from frontend-test frontend-test

test-down:
	$(TEST_COMPOSE) down -v

clean:
	$(APP_COMPOSE) down -v
	$(TEST_COMPOSE) down -v
