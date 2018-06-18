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

"""Representation of a Cloud Pub/Sub Subscription resource."""


class Subscription(object):
    """A subscription resource.

    Args:
      name (str): The name of the subscription. It must have the format
        ``projects/{project}/subscriptions/{subscription}``.
        ``{subscription}`` must start with a letter, and contain only letters
        (``[A-Za-z]``), numbers (``[0-9]``), dashes (``-``), underscores
        (``_``), periods (``.``), tildes (``~``), plus (``+``) or percent signs
        (``%``). It must be between 3 and 255 characters in length, and it must
        not start with ``goog``. Consider using the :meth:`subscription_path`
        method to construct the full subscription name to be supplied as this
        argument.
      topic (str): The name of the topic from which this subscription is
        receiving messages. Format is ``projects/{project}/topics/{topic}``.
      push_config (pubsub_client.types.PushConfig, optional): If push delivery
        is used with this subscription, this field is used to configure it. A
        ``None`` value signifies that the subscriber will pull and ack
        messages using API methods.
      ack_deadline_seconds (int, optional): This value is the maximum time after
        a subscriber receives a message before the subscriber should acknowledge
        the message. After message delivery but before the ack deadline expires
        and before the message is acknowledged, it is an outstanding message and
        will not be delivered again during that time (on a best-effort basis).

        For pull subscriptions, this value is used as the ack deadline.
        The minimum custom deadline you can specify is 10 seconds.
        The maximum custom deadline you can specify is 600 seconds (10 minutes).
        If this parameter is 0, a default value of 10 seconds is used.

        For push delivery, this value is also used to set the request timeout
        for the call to the push endpoint.

        If the subscriber never acknowledges the message, the Cloud Pub/Sub
        system will eventually redeliver the message.
    """

    def __init__(self, name, topic, push_config=None, ack_deadline_seconds=0):
        self._name = name
        self._topic = topic
        self._push_config = push_config
        self._ack_deadline_seconds = ack_deadline_seconds

    @property
    def name(self):
        """The name of the subscription.

        The format is ``projects/{project}/subscriptions/{subscription}``.

        Returns:
          str: The name of the subscription.
        """
        return self._name

    @property
    def topic(self):
        """The name of the topic from which this subscription receives messages.

        The format of the name is ``projects/{project}/topics/{topic}``.

        Returns:
          str: The name of the topic from which this subscription receives
            messages.
        """
        return self._topic

    @property
    def push_config(self):
        """Configuration for push delivery of messages.

        A value of ``None`` signifies that the subscriber will pull and ack
        messages using API methods.

        Returns:
          pubsub_client.types.PushConfig: The push delivery configuration of
            this subscription. If this subscription uses pull delivery instead
            of push delivery, the value ``None`` is returned.
        """
        return self._push_config

    @property
    def ack_deadline_seconds(self):
        """The deadline for a subscriber to acknowledge a received message.

        This value is the maximum time after a subscriber receives a message
        before the subscriber should acknowledge the message. After message
        delivery but before the ack deadline expires and before the message is
        acknowledged, it is an outstanding message and will not be delivered
        again during that time (on a best-effort basis).

        For pull subscriptions, this value is used as the ack deadline.
        The minimum deadline you can specify is 10 seconds.
        The maximum deadline you can specify is 600 seconds (10 minutes).
        If this parameter is 0, the default value of 10 seconds is used.

        For push delivery, this value is also used to set the request timeout
        for the call to the push endpoint.

        If the subscriber never acknowledges the message, the Cloud Pub/Sub
        system will eventually redeliver the message.

        Returns:
          int: The maximum time in seconds after a subscriber receives a message
            before the subscriber should acknowledge the message.
        """
        return self._ack_deadline_seconds
