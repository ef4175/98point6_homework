#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t drop-token .
docker run \
  -it \
  --rm drop-token python -m unittest -v
