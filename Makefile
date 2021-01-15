ORG=926150052987.dkr.ecr.eu-west-1.amazonaws.com
PROJ=k8s-sqs-autoscaler
VERSION=1.1.0

.PHONY=release
release:
	docker build -t ${ORG}/${PROJ} -f Dockerfile .
	docker login
	docker tag ${ORG}/${PROJ}:latest ${ORG}/${PROJ}:${VERSION}
	docker push ${ORG}/${PROJ}:${VERSION}
