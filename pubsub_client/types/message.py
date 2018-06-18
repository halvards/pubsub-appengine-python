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

"""Representation of a Cloud Pub/Sub Message received via a subscription."""

import iso8601


class Message(object):
    """A message containing data and attributes.

    The message payload must not be empty; it must contain either a non-empty
    data field, or at least one attribute.

    The common way to interact with Message objects is to receive them in
    callbacks on subscriptions; most users should never have a need to
    instantiate them by hand.

    .. note::
      This class should not be constructed directly; it is the responsibility of
      ``SubscriberClient`` instances to do so as part of the :meth:`subscribe`
      method.

    Args:
      data (bytes): A bytestring representing the message body.
      attributes (dict[str -> str]): The optional attributes of the message.
      message_id (str): The ID of the message.
      publish_time (str): The date and time the message was published, in the
        format ``YYYY-mm-ddTHH:MM:SS.fffZ``.
      ack_id (str): The ID used to acknowledge receipt of the message.
      subscription (str): The name of the subscription.
      ack_func (Callable[str, list[str]]): A function used to acknowledge
        successful receipt and processing of this message. Takes as arguments
        the name of the subscription and a non-empty list of ``ack_ids``.
      nack_func (str, Callable[list[str]]): A function used to decline to
        acknowledge successful receipt and processing of this message. This will
        cause the message to be re-delivered to the subscription. Takes as
        arguments a list of ``ack_ids`` and the name of the subscription.
    """

    def __init__(self, data, attributes, message_id, publish_time,
                 ack_id, subscription, ack_func, nack_func):
        self._data = data
        self._attributes = (attributes or {})
        self._message_id = message_id
        self._publish_time = iso8601.parse_date(publish_time)
        self._ack_id = ack_id
        self._subscription = subscription
        self._ack_func = ack_func
        self._nack_func = nack_func

    @property
    def data(self):
        """The message payload.

        Returns:
          bytes: The message data. This is always a bytestring; if you want a
            text string, call :meth:`bytes.decode`.
        """
        return self._data

    @property
    def attributes(self):
        """The optional attributes of the Cloud Pub/Sub Message.

        Returns:
          dict[str -> str]: The attributes of the message.
            If the message has no attributes, this method returns an empty dict.
        """
        return self._attributes

    @property
    def message_id(self):
        """The ID of this message.

        This ID is assigned by the server when the message is published, and the
        value is guaranteed to be unique within the topic.

        This value may be read by a subscriber that receives a
        :class:`~pubsub_client.Message` object as an argument to a ``callback``
        function via a pull subscription. It must not be populated by the
        publisher in a ``publish`` call.

        Returns:
          str: The message ID assigned by the server.
        """
        return self._message_id

    @property
    def publish_time(self):
        """The time that the message was originally published.

        This value is populated by the server when it receives the ``publish`
        call. It must not be populated by the publisher in a ``publish`` call.

        Returns:
          datetime: The date and time that the message was published.
        """
        return self._publish_time

    def ack(self):
        """Acknowledge the given message.

        Acknowledging a message in Cloud Pub/Sub means that you are done with
        it, and it will not be delivered to this subscription again. You should
        avoid acknowledging messages until you have *finished* processing them,
        so that in the event of a failure, you receive the message again.

        .. warning::
          Acks in Cloud Pub/Sub are best effort. You should always ensure that
          your processing code is idempotent, as you may receive any given
          message more than once.
        """
        self._ack_func(self._subscription, [self._ack_id])

    def nack(self):
        """Decline to acknowldge the given message.

        This will cause the message to be re-delivered to the subscription.
        """
        self._nack_func(self._subscription, [self._ack_id])
