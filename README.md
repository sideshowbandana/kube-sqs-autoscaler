# k8s-sqs-autoscaler
Kubernetes pod autoscaler based on queue size in AWS SQS

## Usage
Create a kubernetes deployment like this:
```
apiVersion: extensions/v1beta1
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
      annotations:
        prometheus.io/scrape: 'true'
        prometheus.io/port: '8080' #Same as prometheus-port option. Default: 8080
    spec:
      containers:
      - name: my-k8s-autoscaler
        image: sideshowbandana/k8s-sqs-autoscaler:1.0.0
        command:
          - ./k8s-sqs-autoscaler
          - --sqs-queue-url=https://sqs.$(AWS_REGION).amazonaws.com/$(AWS_ID)/$(SQS_QUEUE) # required
          - --kubernetes-deployment=$(KUBERNETES_DEPLOYMENT)
          - --kubernetes-namespace=$(K8S_NAMESPACE) # optional
          - --aws-region=eu-west-1  #required
          - --poll-period=10 # optional
          - --scale-down-cool-down=30 # optional
          - --scale-up-cool-down=10 # optional
          - --scale-up-messages=20 # optional
          - --scale-down-messages=10 # optional
          - --max-pods=30 # optional
          - --min-pods=1 # optional
          - --prometheus-port=8080 #optional
          - --queues-to-monitor=SQS_QUEUE_1,SQS_QUEUE2 #required
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
        - containerPort: 8080

```
