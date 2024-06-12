#!/bin/sh

set -e

poetry run alembic upgrade head

# You can put other setup logic here
# Evaluating passed command:
eval "exec poetry run $@"
