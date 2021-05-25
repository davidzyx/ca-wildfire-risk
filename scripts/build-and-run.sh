#!/bin/bash

set -ex

docker build -t fire .

docker run --rm -it -p 8050:8050 -e PYTHONPATH=/app fire
