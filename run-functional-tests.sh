#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t drop-token .
docker run \
  -it \
  -e WIN_CONDITION=4 \
  --rm drop-token pytest -v functional_tests
