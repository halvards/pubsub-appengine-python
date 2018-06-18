#!/usr/bin/env bash

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

set -euo pipefail

echo 'Generating source for running the same tests with the google-cloud-pubsub client library'

pip install -I google-cloud-pubsub=="$(curl -Ls https://pypi.org/pypi/google-cloud-pubsub/json | jq -r '.info.version')" > /dev/null

sed 's/import pubsub_client as pubsub/from google.cloud import pubsub/' tests/test_pubsub_client.py > tests/test_google_cloud_pubsub_generated.py

sed -i.bak 's/TestPubSubClient/TestGoogleCloudPubSub/' tests/test_google_cloud_pubsub_generated.py
rm tests/test_google_cloud_pubsub_generated.py.bak

echo -e 'Now run all tests using\n    python -m unittest discover'
