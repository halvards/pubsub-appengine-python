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

"""Representation of a Cloud Pub/Sub Topic resource."""


class Topic(object):
    """A topic resource.

    Args:
      name (str): The name of the topic. It must have the format
        ``projects/{project}/topics/{topic}``. ``{topic}`` must start with a
        letter, and contain only letters (``[A-Za-z]``), numbers (``[0-9]``),
        dashes (``-``), underscores (``_``), periods (``.``), tildes (``~``),
        plus (``+``) or percent signs (``%``). It must be between 3 and 255
        characters in length, and it must not start with ``goog``.
    """

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """The name of the topic.

        The format of the name is ``projects/{project}/topics/{topic}``.

        Returns:
          str: The name of the topic.
        """
        return self._name
