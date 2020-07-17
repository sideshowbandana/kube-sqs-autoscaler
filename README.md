# k8s-sqs-autoscaler
Kubernetes pod autoscaler based on queue size in AWS SQS

# Note, this is heavily modified to support scaling based on average messages per pod rather than total messages

## Usage
Create a kubernetes deployment like this:
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-k8s-autoscaler
spec:
  revisionHistoryLimit: 1
  replicas: 1
  template:
    metadata:
      labels:
        app: my-k8s-autoscaler
    spec:
      containers:
      - name: my-k8s-autoscaler
        image: sideshowbandana/k8s-sqs-autoscaler:1.0.0
        command:
          - ./k8s-sqs-autoscaler
          - --sqs-queue-name=${SQS_QUEUE_NAME}
          - --kubernetes-deployment=$(KUBERNETES_DEPLOYMENT)
          - --kubernetes-namespace=$(K8S_NAMESPACE) # (optional)
          - --aws-region=${AWS_REGION}  # (required)
          - --poll-period=60 # optional
          - --scale-down-cool-down=30 # seconds (optional)
          - --scale-up-cool-down=10 # seconds (optional)
          - --scale-up-messages=20 # average messages per pod (optional)
          - --scale-down-messages=10 # average messages per pod (optional)
          - --max-pods=30 # (optional)
          - --min-pods=1 # (optional)
        env:
          - name: AWS_REGION
            value: us-east-1
          - name: K8S_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
          - name: KUBERNETES_DEPLOYMENT
            value: my-k8s-app
          - name: SQS_QUEUE_NAME
            value: sqs-queue-name
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "1512Mi"
            cpu: "500m"
        ports:
        - containerPort: 80
```
