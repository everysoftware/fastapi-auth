APP_PATH = app
TESTS_PATH = tests
LOGS_SINCE = 10m

.PHONY: run
run:
	docker-compose up db redis -d
	uvicorn $(APP_PATH):app --host 0.0.0.0 --port 8000 --log-config logging.yaml

.PHONY: up
up:
	docker-compose up --build -d

.PHONY: up-prod
up-prod:
	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --build -d

.PHONY: logs
logs:
	docker-compose logs --since $(LOGS_SINCE) --follow

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
	docker-compose up db -d
	alembic revision --autogenerate

PHONY: upgrade
upgrade:
	docker-compose up db -d
	alembic upgrade head

PHONY: downgrade
downgrade:
	docker-compose up db -d
	alembic downgrade -1

# Windows only
PHONY: kill
kill:
	TASKKILL /F /IM python.exe
