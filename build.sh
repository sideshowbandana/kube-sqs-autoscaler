#!/bin/bash
pushd $(dirname $0)
CURRENT_COMMIT=$( git rev-parse HEAD | cut -c 1-10 )
docker build -t docker.io/stops/k8s-sqs-autoscaler:${CURRENT_COMMIT} .
echo "Done."
popd
