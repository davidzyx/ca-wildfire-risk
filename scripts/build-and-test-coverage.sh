#!/bin/bash

set -ex

docker build -t fire .

docker run --rm fire python -m pytest --headless --cov=src tests/
