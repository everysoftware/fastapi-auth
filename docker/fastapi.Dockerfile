ARG APP_NAME=app
ARG APP_PATH=/opt/$APP_NAME
ARG PYTHON_VERSION=3.12-bullseye
ARG POETRY_VERSION=1.8.2

#
# Stage: staging
#

FROM python:$PYTHON_VERSION AS staging
ARG APP_NAME
ARG APP_PATH
ARG POETRY_VERSION

# Python process will be ran only once in the container
# so we don’t need to write the compiled Python storage (*.pyc) to disk
# Make sure Python outputs are sent straight to terminal
# Make sure Python traceback are dumped (even on segfaults for instance)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

# We won’t update the pip version in any case
# Default timeout is only 15 seconds
# Fixing Poetry version
# Instead of /root
# Make sure the .venv directory will be in the build directory
# No prompt from Poetry
# Path for building stages
# Add the virtual environment to path in a separate ENVline to use previously defined environment variables.
# Update path with Poetry and virtual env path.
ENV POETRY_VERSION=$POETRY_VERSION
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Import our project storage
WORKDIR $APP_PATH
COPY ./poetry.lock ./pyproject.toml ./
COPY ./$APP_NAME ./$APP_NAME

#
# Stage: build
#
FROM staging as build
ARG APP_PATH

WORKDIR $APP_PATH

# Create a dummy README.md file
RUN touch README.md
# Build wheel
RUN poetry build --format wheel
# Export requirements
RUN poetry export --format requirements.txt --output requirements.txt --without-hashes

#
# Stage: production
#
FROM python:$PYTHON_VERSION as production
ARG APP_NAME
ARG APP_PATH

# To show .env file is not needed
ENV NO_ENV_FILE=1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

# Get build artifact wheel and install it respecting dependency versions
WORKDIR $APP_PATH
COPY --from=build $APP_PATH/dist/*.whl ./
RUN pip install ./$APP_NAME*.whl

# Export APP_NAME as environment variable for the CMD
ENV APP_NAME=$APP_NAME

# Migrations
COPY ./alembic.ini ./
COPY ./migrations ./migrations

# Entrypoint script
COPY ./docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn -w 4 -k uvicorn.workers.UvicornWorker \"$APP_NAME:app\" -b 0.0.0.0:8000"]
