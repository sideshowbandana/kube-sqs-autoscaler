import boto3
import os
from time import sleep, time
from logs.log import logger
from kubernetes import client, config
from prometheus_client import start_http_server, Gauge

class SQSPoller:

    options = None
    sqs_client = None
    sqs_resource = None
    apps_v1 = None
    last_message_count = None
 
    def __init__(self, options):
        self.options = options
        self.sqs_client = boto3.client('sqs', region_name=self.options.aws_region)
        self.sqs_resource = boto3.resource('sqs', region_name=self.options.aws_region)
        config.load_incluster_config()
        self.apps_v1 = client.AppsV1Api()
        self.last_scale_up_time = time()
        self.last_scale_down_time = time()
        self.approximate_number_of_messages = Gauge('approximate_number_of_messages', 'Number of messages available', ['queue'])
        self.approximate_number_of_messages_delayed = Gauge('approximate_number_of_messages_delayed', 'Number of messages delayed',['queue'])
        self.approximate_number_of_messages_not_visible = Gauge('approximate_number_of_messages_not_visible','Number of messages in flight', ['queue'])

    def message_count(self):
        response = self.sqs_client.get_queue_attributes(
            QueueUrl=self.options.sqs_queue_url,
            AttributeNames=['ApproximateNumberOfMessages','ApproximateNumberOfMessagesNotVisible']
        )
        totalMessages = int(response['Attributes']['ApproximateNumberOfMessages']) + int(response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
        return totalMessages


    def poll(self):
        message_count = self.message_count()
        t = time()
        if  message_count >= self.options.scale_up_messages:
            if t - self.last_scale_up_time > self.options.scale_up_cool_down:
                self.scale_up()
                self.last_scale_up_time = t
            else:
                logger.debug("Waiting for scale up cooldown")
        if message_count <= self.options.scale_down_messages:
            if t - self.last_scale_down_time > self.options.scale_down_cool_down:
                self.scale_down()
                self.last_scale_down_time = t
            else:
                logger.debug("Waiting for scale down cooldown")

        # code for scale to use msg_count
        

    def scale_up(self):
        deployment = self.deployment()
        if deployment.spec.replicas < self.options.max_pods:
            logger.info("Scaling up")
            deployment.spec.replicas += 1
            self.update_deployment(deployment)
        elif deployment.spec.replicas > self.options.max_pods:
            self.scale_down()
        else:
            logger.info("Max pods reached")

    def scale_down(self):
        deployment = self.deployment()
        if deployment.spec.replicas > self.options.min_pods:
            logger.info("Scaling Down")
            deployment.spec.replicas -= 1
            self.update_deployment(deployment)
        elif deployment.spec.replicas < self.options.min_pods:
            self.scale_up()
        else:
            logger.info("Min pods reached")

    def deployment(self):
        logger.debug("loading deployment: {} from namespace: {}".format(self.options.kubernetes_deployment, self.options.kubernetes_namespace))
        deployments = self.apps_v1.list_namespaced_deployment(self.options.kubernetes_namespace, label_selector="app={}".format(self.options.kubernetes_deployment))
        return deployments.items[0]

    def update_deployment(self, deployment):
        # Update the deployment
        api_response = self.apps_v1.patch_namespaced_deployment(
            name=self.options.kubernetes_deployment,
            namespace=self.options.kubernetes_namespace,
            body=deployment)
        logger.debug("Deployment updated. status='%s'" % str(api_response.status))

   
    def update_metrics(self):
        """
        Updates the values of the prometheus metrics with the values of the attributes from each SQS queue
        """
        queues = self.options.queues_to_monitor.split(",")
        for queue_name in queues:
            q = self.sqs_resource.get_queue_by_name(QueueName=queue_name)
            logger.debug(f"Updating metrics for queue [{queue_name}]")
            self.approximate_number_of_messages.labels(queue=queue_name).set(
                q.attributes.get('ApproximateNumberOfMessages'))
            self.approximate_number_of_messages_not_visible.labels(queue=queue_name).set(
                q.attributes.get('ApproximateNumberOfMessagesNotVisible'))
            self.approximate_number_of_messages_delayed.labels(queue=queue_name).set(
                q.attributes.get('ApproximateNumberOfMessagesDelayed'))

    def run(self):
        options = self.options
        start_http_server(self.options.prometheus_port)
        logger.debug("Starting poll for {} every {}s".format(options.sqs_queue_url, options.poll_period))
        logger.info("Started metrics exporter at port 9095")
        while True:
            self.poll()
            self.update_metrics()
            sleep(self.options.poll_period)

def run(options):
    """
    poll_period is set as as part of k8s deployment env variable
    sqs_queue_url is set as as part of k8s deployment env variable
    """
    SQSPoller(options).run()
