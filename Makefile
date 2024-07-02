DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker_compose/app.yaml
APP_CONTAINER = it_call-main-app
STORAGES_FILE = docker_compose/storages.yaml
DB_CONTAINER = postgres-it_call

.PHONY: app
app:
	${DC} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: storages
storages:
	${DC} -f ${STORAGES_FILE} ${ENV} up --build -d

.PHONY: postgres
postgres:
	${EXEC} ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME} -p ${DB_PORT}

.PHONY: all
all:
	${DC} -f ${STORAGES_FILE} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} -f ${STORAGES_FILE} down

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: migrate
migrate:
	@if [ -z "${name}" ]; then echo "Description is required. Usage: make migrations name=\"description\""; exit 1; fi
	${EXEC} ${APP_CONTAINER} alembic revision --autogenerate -m "${name}"

.PHONY: upgrade
upgrade:
	${EXEC} ${APP_CONTAINER} alembic upgrade head

.PHONY: downgrade
downgrade:
	${EXEC} ${APP_CONTAINER} alembic downgrade -1
