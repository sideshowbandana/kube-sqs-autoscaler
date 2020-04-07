#!/bin/bash -ex
IMAGE_NAME=k8s-sqs-autoscaler
export CURRENT_COMMIT=$( git rev-parse HEAD | cut -c 1-10 )
export REPO="docker.io/stops/${IMAGE_NAME}"
export FULL_IMAGE_NAME="$REPO:$CURRENT_COMMIT"
