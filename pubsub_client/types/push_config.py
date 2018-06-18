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

"""Configuration for push delivery subscriptions."""


class PushConfig(object):
    """Configuration for a push delivery endpoint.

    Args:
      push_endpoint (str): A URL locating the endpoint to which messages
        should be pushed.
    """

    def __init__(self, push_endpoint=''):
        self._push_endpoint = push_endpoint

    @property
    def push_endpoint(self):
        """The URL locating the endpoint to which messages should be pushed.

        For example, a Webhook endpoint might use "https://example.com/push".

        Returns:
          str: The push endpoint URL.
        """
        return self._push_endpoint
