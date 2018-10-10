# k8s-sqs-autoscaler
Kubernetes pod autoscaler based on queue size in AWS SQS

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
  selector:
    matchLabels:
      app: my-k8s-autoscaler
      tier: console  
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
          - --sqs-queue-url=https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ID)/$(SQS_QUEUE) # required
          - --kubernetes-deployment=$(KUBERNETES_DEPLOYMENT)
          - --kubernetes-namespace=$(K8S_NAMESPACE) # optional
          - --aws-region=us-west-2  #required
          - --poll-period=10 # optional
          - --scale-down-cool-down=30 # optional
          - --scale-up-cool-down=10 # optional
          - --scale-up-messages=20 # optional
          - --scale-down-messages=10 # optional
          - --max-pods=30 # optional
          - --min-pods=1 # optional
        env:
          - name: K8S_NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
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
