# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""End-to-end tests for pubsub_client."""

import json
import threading
import unittest
import uuid

import pubsub_client as pubsub

import google.auth


class TestPubSubClient(unittest.TestCase):
    _project = None       # type: str
    _publisher = None     # type: pubsub.PublisherClient
    _subscriber = None    # type: pubsub.SubscriberClient
    _topic = None         # type: pubsub.types.Topic
    _subscription = None  # type: pubsub.types.Subscription

    @classmethod
    def setUpClass(cls):
        _, cls._project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/pubsub'])
        cls._publisher = pubsub.PublisherClient()
        cls._subscriber = pubsub.SubscriberClient()
        topic_name = cls._publisher.topic_path(
            project=cls._project, topic='topic-{0}'.format(str(uuid.uuid4())))
        cls._topic = cls._publisher.create_topic(name=topic_name)
        subscription_name = cls._subscriber.subscription_path(
            project=cls._project,
            subscription='subscription-{0}'.format(str(uuid.uuid4())))
        cls._subscription = cls._subscriber.create_subscription(
            name=subscription_name, topic=cls._topic.name)

    @classmethod
    def tearDownClass(cls):
        cls._subscriber.delete_subscription(subscription=cls._subscription.name)
        cls._publisher.delete_topic(topic=cls._topic.name)

    def test_publish_subscribe_byte_string(self):
        data = b'hello'
        subscribe_future = None

        def callback(rcv_message):
            if rcv_message is None:
                self.fail('No message received')
            rcv_message.ack()
            self.assertEqual(rcv_message.data, data)
            threading.Thread(target=subscribe_future.cancel, args=()).start()

        subscribe_future = self._subscriber.subscribe(
            subscription=self._subscription.name, callback=callback)
        message_id_future = self._publisher.publish(
            topic=self._topic.name, data=data)
        message_id = message_id_future.result()
        self.assertIsNotNone(message_id)
        subscribe_future.result()

    def test_publish_subscribe_unicode_string(self):
        data = u'hello'
        subscribe_future = None

        def callback(rcv_message):
            if rcv_message is None:
                self.fail('No message received')
            rcv_message.ack()
            self.assertEqual(rcv_message.data.decode('utf-8'), data)
            threading.Thread(target=subscribe_future.cancel, args=()).start()

        subscribe_future = self._subscriber.subscribe(
            subscription=self._subscription.name, callback=callback)
        message_id_future = self._publisher.publish(
            topic=self._topic.name, data=data.encode('utf-8'))
        message_id = message_id_future.result()
        self.assertIsNotNone(message_id)
        subscribe_future.result()

    def test_publish_subscribe_json(self):
        message_dict = {'mykey': str(uuid.uuid4())}
        message_text = json.dumps(message_dict, ensure_ascii=False)
        subscribe_future = None

        def callback(rcv_message):
            if rcv_message is None:
                self.fail('No message received')
            rcv_message.ack()
            self.assertEqual(rcv_message.data.decode('utf-8'), message_text)
            threading.Thread(target=subscribe_future.cancel, args=()).start()

        subscribe_future = self._subscriber.subscribe(
            subscription=self._subscription.name, callback=callback)
        message_id_future = self._publisher.publish(
            topic=self._topic.name, data=message_text.encode('utf-8'))
        message_id = message_id_future.result()
        self.assertIsNotNone(message_id)
        subscribe_future.result()

    def test_publish_subscribe_multiple_messages(self):
        number_of_messages_to_publish = 3
        messages_received = []
        subscribe_future = None

        def callback(received_message):
            if received_message is None:
                threading.Thread(
                    target=subscribe_future.cancel, args=()).start()
                self.fail('Should not cancel because no message received')
            messages_received.append(received_message.data)
            received_message.ack()
            if len(messages_received) >= number_of_messages_to_publish:
                threading.Thread(
                    target=subscribe_future.cancel, args=()).start()

        subscribe_future = self._subscriber.subscribe(
            subscription=self._subscription.name, callback=callback)

        for _ in range(number_of_messages_to_publish):
            message_id_future = self._publisher.publish(
                topic=self._topic.name, data=b'hello')
            message_id_future.result()

        subscribe_future.result()

    def test_subscription_ack_deadline(self):
        ack_deadline_seconds = 42
        subscription_name = self._subscriber.subscription_path(
            project=self._project,
            subscription='subscription-{0}'.format(str(uuid.uuid4())))
        subscription = None
        try:
            subscription = self._subscriber.create_subscription(
                name=subscription_name,
                topic=self._topic.name,
                ack_deadline_seconds=ack_deadline_seconds)
            self.assertEqual(subscription.ack_deadline_seconds,
                             ack_deadline_seconds)
            self.assertEqual(subscription.push_config.push_endpoint, '')
        finally:
            if subscription is not None:
                self._subscriber.delete_subscription(
                    subscription=subscription.name)

    def test_subscription_push_config(self):
        push_endpoint = 'https://{}.appspot.com/'.format(self._project)
        push_config = pubsub.types.PushConfig(push_endpoint=push_endpoint)
        subscription_name = self._subscriber.subscription_path(
            project=self._project,
            subscription='subscription-{0}'.format(str(uuid.uuid4())))
        subscription = None
        try:
            subscription = self._subscriber.create_subscription(
                name=subscription_name,
                topic=self._topic.name,
                push_config=push_config)
            self.assertEqual(subscription.push_config.push_endpoint,
                             push_config.push_endpoint)
            self.assertEqual(subscription.ack_deadline_seconds, 10)
        finally:
            if subscription is not None:
                self._subscriber.delete_subscription(
                    subscription=subscription.name)


if __name__ == '__main__':
    unittest.main()
