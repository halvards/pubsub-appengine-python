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

"""A Future class to manage background pull subscription of messages."""

from concurrent.futures import ThreadPoolExecutor


class SubscribeFuture(object):
    """Manages the asynchronous execution of pull subscription.

    A background thread is used to poll for messages in a loop, until
    :meth:`cancel()` is called on an unrecoverable error occurs.

    This class conforms to the :class:`concurrent.futures.Future` interface.

    Args:
      subscribe_fn (Callable[str, Callable[~pubsub_client.Message]]): A
        blocking function to pull messages from a subscription and process them
        using a callback function. This function will be run in a loop by this
        future class until this future is cancelled using the :meth:`cancel()`
        method or until an unrecoverable error occurs.
      subscription (str): The name of the subscription. The subscription should
        have already been created (for example, by using
        ``SubScriberClient.create_subscription()``.
      callback (Callable[~pubsub_client.Message]): The callback function. This
        function receives the message as its only argument and will be called
        from a different thread/process depending on the scheduling strategy.
    """

    def __init__(self, subscribe_fn, subscription, callback):
        self._cancelled = False
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._future = self._executor.submit(self._subscribe_loop,
                                             subscribe_fn,
                                             subscription,
                                             callback)

    def _subscribe_loop(self, subscribe_fn, subscription, callback):
        while not self._cancelled:
            subscribe_fn(subscription, callback)

    def cancel(self):
        """See :meth:`concurrent.futures.Future.cancel()`."""
        self._cancelled = True
        self._executor.shutdown(wait=False)
        return self._future.cancel()

    def cancelled(self):
        """See :meth:`concurrent.futures.Future.cancelled()`."""
        return self._cancelled

    def running(self):
        """See :meth:`concurrent.futures.Future.running()`."""
        return self._future.running()

    def done(self):
        """See :meth:`concurrent.futures.Future.done()`."""
        return self._future.done()

    def result(self, timeout=None):
        """See :meth:`concurrent.futures.Future.result()`."""
        return self._future.result(timeout)

    def exception(self, timeout=None):
        """See :meth:`concurrent.futures.Future.exception()`."""
        return self._future.exception(timeout)

    def add_done_callback(self, fn):
        """See :meth:`concurrent.futures.Future.add_done_callback()`."""
        return self._future.add_done_callback(fn)

    def set_running_or_notify_cancel(self):
        """See
            :meth:`concurrent.futures.Future.set_running_or_notify_cancel()`.
        """
        return self._future.set_running_or_notify_cancel()

    def set_result(self, result):
        """See :meth:`concurrent.futures.Future.set_result()`."""
        self._future.set_result(result)

    def set_exception(self, exception):
        """See :meth:`concurrent.futures.Future.set_exception()`."""
        self._future.set_exception(exception)
