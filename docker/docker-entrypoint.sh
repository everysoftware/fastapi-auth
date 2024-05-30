#!/bin/sh

set -e

# You can put other setup logic here
alembic upgrade head

# Evaluating passed command:
eval "exec $@"
