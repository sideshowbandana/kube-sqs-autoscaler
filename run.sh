#!/bin/bash

set -e
set -o nounset
cd $(dirname $0) 

docker build . -t k8s-sqs-autoscaler 

docker run -e AWS_SHARED_CREDENTIALS_FILE=/root/.aws/mfa -e AWS_DEFAULT_REGION=us-east-1 -e KUBECONFIG=/root/.creds/prod/us-east-1c -ti -v $(pwd):/usr/src/app -v ~/src/kube2/tool/.creds:/root/.creds -v ~/.aws:/root/.aws k8s-sqs-autoscaler $*
