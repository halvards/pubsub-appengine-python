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

"""Sample client for interacting with Cloud Pub/Sub topics."""

import base64

import google.auth
from concurrent.futures import ThreadPoolExecutor
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient import discovery
from googleapiclient import http
from six import binary_type
from six.moves.urllib.parse import quote_plus

from pubsub_client.types import Topic


class PublisherClient(object):
    """A publisher client for Google Cloud Pub/Sub.

    This creates an object that is capable of publishing messages. Generally,
    you can instantiate this client with no arguments, and you get sensible
    defaults.

    Args:
      credentials (~google.auth.credentials.Credentials, optional): The
        credentials to authenticate to the Cloud Pub/Sub API. Application
        Default Credentials or the value of the environment variable
        ``GOOGLE_APPLICATION_CREDENTIALS`` will be used if no credential object
        is supplied as an argument.
      executor (~concurrent.futures.Executor, optional): An object that can
        execute calls to publish messages asynchronously. A
        :class:`~concurrent.futures.ThreadPoolExecutor` with the default number
        of `max_workers` (`(multiprocessing.cpu_count() or 1) * 5`) will be used
        if an executor is not supplied.
      num_retries (int, optional): Number of times to retry with randomized
        exponential backoff. If all retries fail, the raised HttpError
        represents the last request. If zero (default), we attempt the request
        only once. For the exact rules determining whether retries are
        attempted, see the method
        :meth:`googleapiclient.http._should_retry_response()`.
    """

    def __init__(self, credentials=None, executor=None, num_retries=2):
        self._num_retries = (num_retries or 0)
        if credentials is None:
            credentials, _ = google.auth.default(
                scopes=['https://www.googleapis.com/auth/pubsub'])

        def _request_builder(_, *args, **kwargs):
            return http.HttpRequest(AuthorizedHttp(credentials=credentials),
                                    *args, **kwargs)

        self._client = discovery.build(
            serviceName='pubsub', version='v1', requestBuilder=_request_builder)
        self._executor = (executor or ThreadPoolExecutor())

    @classmethod
    def topic_path(cls, project, topic):
        """Creates a fully-qualified topic resource name string.

        The format will be ``projects/{project}/topics/{topic}``.

        Args:
          project (str): The Google Cloud project ID
          topic (str): The short-form name of the topic. This argument will be
            quoted so it is URL-safe.

        Returns:
          str: The fully-qualified topic resource name.
        """
        return 'projects/{}/topics/{}'.format(project, quote_plus(topic))

    def create_topic(self, name, num_retries=None):
        """Creates a topic resource with the given name.

        Example:

        .. code-block:: python

          import pubsub_client as pubsub
          client = pubsub.PublisherClient()
          topic_name = client.topic_path('[PROJECT]', '[TOPIC]')
          topic = client.create_topic(topic_name)

        Args:
          name (str): The name of the topic. It must have the format
            ``projects/{project}/topics/{topic}``. ``{topic}`` must start with
            a letter, and contain only letters (``[A-Za-z]``), numbers
            (``[0-9]``), dashes (``-``), underscores (``_``), periods (``.``),
            tildes (``~``), plus (``+``) or percent signs (``%``). It must be
            between 3 and 255 characters in length, and it must not start with
            ``goog``. Consider using the :meth:`topic_path` method to construct
            the full topic name to be supplied as this argument.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.

        Returns:
          pubsub_client.Topic: A topic instance.
        """
        body = {'name': name}
        response = self._client.projects().topics().create(
            name=name, body=body).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))
        return Topic(name=response['name'])

    def delete_topic(self, topic, num_retries=None):
        """Deletes the topic resource with the given name.

        After a topic is deleted, a new topic may be created with the same name;
        this is an entirely new topic with none of the old configuration or
        subscriptions. Existing subscriptions to this topic are not deleted, but
        their ``topic`` field is set to ``_deleted-topic_``.

        Example:

        .. code-block:: python

          import pubsub_client as pubsub
          client = pubsub.PublisherClient()
          topic_name = client.topic_path('[PROJECT]', '[TOPIC]')
          client.delete_topic(topic_name)

        Args:
          topic (str): Name of the topic to delete.
            Format is ``projects/{project}/topics/{topic}``.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.
        """
        self._client.projects().topics().delete(topic=topic).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))

    def _publish(self, topic, data, num_retries=None, **attrs):
        """Synchronously publish a single message.

        This method blocks until the message has been successfully published.
        Use via the non-blocking :meth:`publish` method below.

        Args:
          topic (str): The topic to publish the message to.
          data (bytes): A bytestring representing the message body.
          num_retries (int, optional): Number of times to retry with randomized
            exponential backoff. If specified, overrides the value provided to
            :meth:`__init__()`.
          **attrs (Mapping[str, str]): An optional dictionary of attributes to
            be sent as metadata. (These may be text strings or bytestrings.)

        Returns:
          string: The ID assigned to the published message by the server.
        """
        if not isinstance(data, binary_type):
            raise TypeError('Data must be sent as a bytestring.')
        message = {'data': base64.b64encode(data).decode('utf-8'),
                   'attributes': attrs}
        body = {'messages': [message]}
        response = self._client.projects().topics().publish(
            topic=topic, body=body).execute(
            num_retries=(self._num_retries if num_retries is None
                         else num_retries))
        return response['messageIds'][0]

    def publish(self, topic, data, **attrs):
        """Asynchronously publish a single message.

        .. note::
          Messages in Cloud Pub/Sub are blobs of bytes. They are *binary* data,
          not text. You must send data as a bytestring (``str`` in Python 2;
          ``bytes`` in Python 3), and this library will raise an exception if
          you send a text string.

          The reason that this is so important (and why we do not try to coerce
          for you) is because Cloud Pub/Sub is also platform independent and
          there is no way to know how to decode messages properly on the other
          side; therefore, encoding and decoding is a required exercise for the
          developer.

        Example:

        .. code-block:: python

          import pubsub_client as pubsub
          client = pubsub.PublisherClient()
          topic = client.topic_path('[PROJECT]', '[TOPIC]')
          data = u'My important message.'.encode('utf-8')
          message_id_future = client.publish(topic, data, username='guido')

        Args:
          topic (str): The topic to publish the message to.
          data (bytes): A bytestring representing the message body.
          **attrs (Mapping[str, str]): An optional dictionary of attributes to
            be sent as metadata. (These may be text strings or bytestrings.)

        Returns:
          ~concurrent.futures.Future: An object conforming to the
            ``concurrent.futures.Future`` interface that resolves to the server
            assigned message ID once the message has been successfully
            published.
        """
        return self._executor.submit(self._publish, topic, data, **attrs)
