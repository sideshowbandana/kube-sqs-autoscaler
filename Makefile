ORG=133072409765.dkr.ecr.eu-west-1.amazonaws.com
PROJ=k8s-sqs-autoscaler
VERSION=1.0.2

.PHONY=release
release:
	docker build -t ${ORG}/${PROJ} -f Dockerfile .
	docker login
	docker tag ${ORG}/${PROJ}:latest ${ORG}/${PROJ}:${VERSION}
	docker push ${ORG}/${PROJ}:${VERSION}
