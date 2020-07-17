import pytest
from time import time
from munch import munchify

from sqs.sqs import SQSPoller


def deployment():
    return munchify({
        'spec': {
            'replicas': 10
        }
    })


@pytest.fixture
def options():
    return munchify({'aws_region': 'us-east-1',
                     'kubernetes_deployment': 'test-app',
                     'kubernetes_namespace': 'default',
                     'sqs_queue_url': 'test-queue-url',
                     'scale_up_messages': 20,
                     'scale_down_messages': 5,
                     'scale_up_cool_down': 60,
                     'scale_down_cool_down': 120,
                     'min_pods': 2,
                     'max_pods': 30,
                     'poll_period': 10})


@pytest.fixture
def patched(mocker):
    mocker.patch('sqs.sqs.config')
    mocker.patch('sqs.sqs.client')
    mocker.patch('sqs.sqs.boto3')
    mocker.patch('sqs.sqs.sleep')
    mocker.patch.object(SQSPoller, '_deployment', deployment())
    mocker.patch.object(SQSPoller, 'message_count', return_value=10)


def test_init_with_queue_url(patched, options):
    client = SQSPoller(options)
    assert client.options.sqs_queue_url == 'test-queue-url'


def test_init_with_queue_name(patched, options):
    options.sqs_queue_url = None
    options.sqs_queue_name = 'queue-name'
    client = SQSPoller(options)
    client.sqs_client.get_queue_url.assert_called_with(QueueName='queue-name')


def test_poll_no_scale(patched, options):
    client = SQSPoller(options)
    client.poll()
    assert client._deployment.spec.replicas == 10


@pytest.mark.parametrize('messages,offset,expected', [
    (1000, 200, 30),  # Should hit max
    (1000, 1, 10),  # Recently scaled should stay
    (1, 200, 2),  # Should hit min,
    (45, 1, 10),  # Recently scaled should stay
    (250, 200, 13),  # Should scale up to specific number
    (40, 200, 8),  # Should scale down to specific number
])
def test_poll_scale_up(messages, offset, expected, patched, options):
    client = SQSPoller(options)
    client.message_count.return_value = messages
    client.last_scale_up_time = client.last_scale_down_time = time() - offset
    client.poll()
    assert client._deployment.spec.replicas == expected
