#!/usr/bin/env bash

DOCKER_BUILDKIT=1 docker build -t drop-token .
docker run \
  -it \
  -e WIN_CONDITION=4 \
  -p 8000:80 \
  --rm drop-token uvicorn --host=0.0.0.0 --port=80 main:app
