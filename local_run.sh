#!/bin/bash -x

set -e
set -o nounset

pushd $(dirname $0)
ROOT_DIR=$(pwd)
source env.sh || exit 1
source build.sh || exit 1

CONTAINER_NAME=${IMAGE_NAME}

docker run -d -it --rm \
  -v ~/.aws/credentials:/root/.aws/credentials \
  --name $CONTAINER_NAME ${FULL_IMAGE_NAME} bash
popd