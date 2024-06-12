#!/bin/sh

set -e

alembic upgrade head

# You can put other setup logic here
# Evaluating passed command:
eval "exec $@"
