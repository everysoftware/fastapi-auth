APP_PATH = app
TESTS_PATH = tests
LOGS_SINCE = 10m

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: run
run:
	docker-compose up db redis -d
	uvicorn $(APP_PATH):app --host 0.0.0.0 --port 8000

.PHONY: up
up:
	docker-compose up --build -d

.PHONY: up-prod
up-prod:
	docker-compose up -f docker-compose.yml -f docker-compose-prod.yml --build -d

.PHONY: db
db:
	docker-compose exec -it db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

.PHONY: logs
logs:
	docker-compose logs --since LOGS_SINCE --follow

.PHONY: stop
stop:
	docker-compose stop

.PHONY: restart
restart:
	docker-compose restart

.PHONY: format
format:
	ruff format $(APP_PATH) $(TESTS_PATH)

.PHONY: lint
lint:
	ruff check $(APP_PATH) $(TESTS_PATH) --fix
	mypy $(APP_PATH) --install-types --enable-incomplete-feature=NewGenericSyntax

PHONY: generate
generate:
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up db -d
	alembic revision --autogenerate

PHONY: upgrade
upgrade:
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up db -d
	alembic upgrade head

PHONY: downgrade
downgrade:
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up db -d
	alembic downgrade -1

PHONY: test
test:
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up db -d
	pytest $(TESTS_PATH) -s -v

# Only for windows
PHONY: kill
kill:
	TASKKILL /F /IM python.exe
