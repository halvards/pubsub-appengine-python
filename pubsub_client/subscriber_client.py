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

"""Sample client for interacting with Cloud Pub/Sub subscriptions."""

import base64

import google.auth
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient import discovery
from googleapiclient import http
from six.moves.urllib.parse import quote_plus

from pubsub_client.types import Message
from pubsub_client.types import PushConfig
from pubsub_client.types import SubscribeFuture
from pubsub_client.types import Subscription


class SubscriberClient(object):
    """A subscriber client for Google Cloud Pub/Sub.

    This creates an object that is capable of subscribing to messages.
    Generally, you can instantiate this client with no arguments, and you get
    sensible defaults.

    Args:
      credentials (~google.auth.credentials.Credentials, optional): The
        credentials to authenticate to the Cloud Pub/Sub API. Application
        Default Credentials or the value of the environment variable
        ``GOOGLE_APPLICATION_CREDENTIALS`` will be used if no credential object
        is supplied as an argument.
      num_retries (int, optional): Number of times to retry with randomized
        exponential backoff. If all retries fail, the raised HttpError
        represents the last request. If zero (default), we attempt the request
        only once. For the exact rules determining whether retries are
        attempted, see the method
        :meth:`googleapiclient.http._should_retry_response()`.
    """

    def __init__(self, credentials=None, num_retries=2):
        self._num_retries = (num_retries or 0)
        if credentials is None:
            credentials, _ = google.auth.default(
                scopes=['https://www.googleapis.com/auth/pubsub'])

        def _request_builder(_, *args, **kwargs):
            return http.HttpRequest(AuthorizedHttp(credentials=credentials),
                                    *args, **kwargs)

        self._client = discovery.build(
            serviceName='pubsub', version='v1', requestBuilder=_request_builder)

    @classmethod
    def subscription_path(cls, project, subscription):
        """Creates a fully-qualified subscription resource name string.

        The format will be ``projects/{project}/subscriptions/{subscription}``.

        Args:
          project (str): The Google Cloud project ID
          subscription (str): The short-form name of the subscription. This
            argument will be quoted so it is URL-safe.

        Returns:
          str: The fully-qualified subscription resource name.
        """
        return 'projects/{}/subscriptions/{}'.format(project,
                                                     quote_plus(subscription))

    def create_subscription(self, name, topic, push_config=None,
                            ack_deadline_seconds=0, num_retries=None):
        """Creates a subscription resource on a given topic.

        Example:

        .. code-block:: python

          import pubsub_client as pubsub

          client = pubsub.SubscriberClient()

          name = client.subscription_path('[PROJECT]', '[SUBSCRIPTION]')

          topic = client.topic_path('[PROJECT]', '[TOPIC]')

          subscription = client.create_subscription(name, topic)

        Args:
          name (str): The name of the subscription. It must have the format
            ``projects/{project}/subscriptions/{subscription}``.
            ``{subscription}`` must start with a letter, and contain only
            letters (``[A-Za-z]``), numbers (``[0-9]``), dashes (``-``),
            underscores(``_``), periods (``.``), tildes (``~``), plus (``+``) or
            percent signs (``%``). It must be between 3 and 255 characters in
            length, and it must not start with ``goog``. Consider using the
            :meth:`subscription_path` method to construct the full subscription
            name to be supplied as an argument.
          topic (str): The name of the topic from which this subscription is
            receiving messages. Format is ``projects/{project}/topics/{topic}``.
          push_config (pubsub_client.types.PushConfig, optional): If push
            delivery is used with this subscription, this field is used to
            configure it. A ``None`` value signifies that the subscriber will
            pull and ack messages using API methods.
          ack_deadline_seconds (int, optional): This value is the maximum time
            after a subscriber receives a message before the subscriber should
            acknowledge the message. After message delivery but before the ack
            deadline expires and before the message is acknowledged, it is an
            outstanding message and will not be delivered again during that time
            (on a best-effort basis).

            For pull subscriptions, this value is used as the ack deadline.
            The minimum deadline you can specify is 10 seconds.
            The maximum deadline you can specify is 600 seconds (10 minutes).
            If this parameter is 0, the default value of 10 seconds is used.

            For push delivery, this value is also used to set the request
            timeout for the call to the push endpoint.

            If the subscriber never acknowledges the message, the Cloud Pub/Sub
            system will eventually redeliver the message.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.

        Returns:
          pubsub_client.Subscription: A subscription instance.
        """
        body = {'name': name,
                'ackDeadlineSeconds': ack_deadline_seconds,
                'topic': topic}
        if push_config is not None and push_config.push_endpoint:
            body['pushConfig'] = {'pushEndpoint': push_config.push_endpoint}
        response = self._client.projects().subscriptions().create(
            name=name, body=body).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))
        subscription_push_config = PushConfig()
        if ('pushConfig' in response and
                'pushEndpoint' in response['pushConfig']):
            push_endpoint = response['pushConfig']['pushEndpoint']
            subscription_push_config = PushConfig(push_endpoint=push_endpoint)
        return Subscription(name=response['name'],
                            topic=response['topic'],
                            push_config=subscription_push_config,
                            ack_deadline_seconds=response['ackDeadlineSeconds'])

    def delete_subscription(self, subscription, num_retries=None):
        """Deletes an existing subscription resource.

        All messages retained in the subscription are immediately dropped.

        After a subscription is deleted, a new one may be created with the same
        name, but the new one has no association with the old subscription.

        Example:

        .. code-block:: python

          import pubsub_client as pubsub

          client = pubsub.SubscriberClient()

          subscription = client.subscription_path('[PROJECT]', '[SUBSCRIPTION]')

          client.delete_subscription(subscription)

        Args:
          subscription (str): The subscription to delete.
            Format is ``projects/{project}/subscriptions/{sub}``.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.
        """
        self._client.projects().subscriptions().delete(
            subscription=subscription).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))

    def acknowledge(self, subscription, ack_ids, num_retries=None):
        """Acknowledges the messages associated with the ``ack_ids``.

        The Cloud Pub/Sub system can remove the relevant messages from the
        subscription.

        Acknowledging a message whose ack deadline has expired may succeed, but
        such a message may be redelivered later. Acknowledging a message more
        than once will not result in an error.

        Args:
          subscription (str): The subscription whose messages are being
            acknowledged. Format is ``projects/{project}/subscriptions/{sub}``.
          ack_ids (list[str]): The acknowledgment IDs of the messages to be
            acknowledged.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.
        """
        body = {'ackIds': ack_ids}
        self._client.projects().subscriptions().acknowledge(
            subscription=subscription, body=body).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))

    def _nack(self, subscription, ack_ids, num_retries=None):
        """Decline to acknowledge the messages associated with the ``ack_ids``.

        This will cause the messages to be re-delivered to the subscription.

        Args:
          subscription (str): The subscription whose messages are being nacked.
            Format is ``projects/{project}/subscriptions/{sub}``.
          ack_ids (list[str]): The acknowledgment IDs of the messages to be
            nacked.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.
        """
        body = {'ackIds': ack_ids, 'ackDeadlineSeconds': 0}
        self._client.projects().subscriptions().modifyAckDeadline(
            subscription=subscription, body=body).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))

    def _subscribe(self, subscription, callback=None, num_retries=None):
        """Synchronously pull a single message from the given subscription.

        The message pulled from the subscription is processed synchronously by
        the provided ``callback`` function.

        This method blocks until the message has been successfully received. Use
        via the non-blocking :meth:`subscribe` method below.

        Args:
          subscription (str): The name of the subscription. The subscription
            should have already been created (for example, by using the
            :meth:`create_subscription` method).
          callback (Callable[~pubsub_client.Message]): The callback function.
            This function receives the message as its only argument and will be
            called from a different thread/process depending on the scheduling
            strategy.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.
        """
        body = {'returnImmediately': False, 'maxMessages': 1}
        response = self._client.projects().subscriptions().pull(
            subscription=subscription, body=body).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))
        if (callback is not None and
                response and
                'receivedMessages' in response and
                response['receivedMessages']):
            received_message = response['receivedMessages'][0]
            data = base64.b64decode(
                received_message['message']['data'].encode('utf-8'))
            attributes = {}
            if 'attributes' in received_message['message']:
                attributes = received_message['message']['attributes']
            callback(
                Message(data=data,
                        attributes=attributes,
                        message_id=received_message['message']['messageId'],
                        publish_time=received_message['message']['publishTime'],
                        ack_id=received_message['ackId'],
                        subscription=subscription,
                        ack_func=self.acknowledge,
                        nack_func=self._nack))

    def subscribe(self, subscription, callback=None):
        """Asynchronously start receiving messages on a given subscription.

        This non-blocking method pulls messages from a Cloud Pub/Sub
        subscription in the background according to the
        :class:`~concurrent.futures.Executor` provided when this client was
        created and schedules them to be processed using the provided
        ``callback``.

        The ``callback`` will be called with an individual
        :class:`pubsub_client.Message`. It is the responsibility of the callback
        to either call ``ack()`` or ``nack()`` on the message when it finished
        processing. If an exception occurs in the callback during processing,
        the exception should be logged and the message should be ``nack()`` ed.

        This method starts the receiver in the background and returns a
        :class:`~concurrent.futures.Future` representing its execution. Waiting
        on the future (calling ``result()``) will block forever or until a
        non-recoverable error is encountered (such as loss of network
        connectivity). Cancelling the future will signal the process to shutdown
        gracefully and exit.

        Example:

        .. code-block:: python

          import pubsub_client as pubsub

          client = pubsub.SubscriberClient()

          # existing subscription
          subscription = client.subscription_path('[PROJECT]', '[SUBSCRIPTION]')

          def callback(message):
            print(message.data)
            message.ack()

          future = client.subscribe(subscription, callback)

          try:
            future.result()
          except KeyboardInterrupt:
            future.cancel()

        Args:
          subscription (str): The name of the subscription. The subscription
            should have already been created (for example, by using the
            :meth:`create_subscription` method).
          callback (Callable[~pubsub_client.Message]): The callback function.
            This function receives the message as its only argument and will be
            called from a different thread or process depending on the
            scheduling strategy (the :class:`~concurrent.futures.Executor` used
            by this client).

        Returns:
          ~concurrent.futures.Future: An object conforming to the
            :class:`concurrent.futures.Future` interface that can be used to
            manage the asynchronous receiving of messages.
        """
        return SubscribeFuture(self._subscribe, subscription, callback)
