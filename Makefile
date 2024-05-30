APP_NAME = app
TESTS_PATH = tests

.PHONY: freeze
freeze:
	pip freeze > requirements.txt

.PHONY: run-dev
run-dev:
	docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up --build -d
	uvicorn $(APP_NAME):app --host 0.0.0.0 --port 8000 --reload

.PHONY: run-prod
run-prod:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml up --build -d

.PHONY: stop-prod
stop-prod:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml stop

.PHONY: format
format:
	ruff format $(APP_NAME) $(TESTS_PATH)

.PHONY: lint
lint:
	ruff check $(APP_NAME) $(TESTS_PATH) --fix
	mypy $(APP_NAME) --install-types

PHONY: generate
generate:
	docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up --build -d
	alembic revision --autogenerate

PHONY: upgrade
upgrade:
	docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up --build -d
	alembic upgrade head

PHONY: downgrade
downgrade:
	docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up --build -d
	alembic downgrade -1

PHONY: check
check:
	docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up --build -d
	pytest $(TESTS_PATH) -v

PHONY: test
test:
	docker-compose -f docker-compose-base.yml -f docker-compose-dev.yml up --build -d
	pytest $(TESTS_PATH) -s -v

PHONY: kill
kill:
	TASKKILL /F /IM python.exe
