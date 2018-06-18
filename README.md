# pubsub-appengine-python [![CircleCI](https://circleci.com/gh/halvards/pubsub-appengine-python.svg?style=svg)](https://circleci.com/gh/halvards/pubsub-appengine-python)

This repository contains sample code that demonstrates how to build a
[Google Cloud Pub/Sub](https://cloud.google.com/pubsub/docs/overview) client
for Python 2.7 and
[Google App Engine Python Standard Environment](https://cloud.google.com/appengine/docs/standard/python/)
based on the
[Google API Client for Python](https://developers.google.com/api-client-library/python/).

This sample code aims to closely mimic the Pub/Sub functionality of the
[Google Cloud Client Libraries for Python](https://google-cloud-python.readthedocs.io/en/latest/pubsub/index.html),
and tests are run to ensure application code written to use this
sample code can work with the official libraries simply by changing the
`import` statement. 

The differences compared to the Google Cloud Client Libraries for Python are as
follows:

- This sample code currently only supports Python 2.7. 
- The [REST/HTTP API](https://cloud.google.com/pubsub/docs/reference/rest/) is
  used instead of the 
  [gRPC API](https://cloud.google.com/pubsub/docs/reference/rpc/).
- Messages are published asynchronously but one by one rather than in batches.
- Messages received on pull subscriptions are processed in the background but
  serially, there is currently no support for multi-threaded pull subscriptions.
- Errors raised are not translated to the error types of the Google Cloud
  Client Libraries for Python. Instead, the errors are passed through from the
  underlying Google API Client Library for Python.
- The retry implementation of the underlying Google API Client Library for
  Python is used for retrying failed API requests, instead of the
  implementation in the Google Cloud Client Libraries for Python. 
- Not all methods of the Pub/Sub client in the Google Cloud Client Libraries
  for Python are implemented in this sample code. Adding missing methods should
  be straightforward, following the patterns already used in this codebase.

## Authentication

This sample code is written for App Engine Python Standard Environment
applications and by default relies on
[Application Default Credentials](https://cloud.google.com/docs/authentication/production)
for authenticating to Cloud Pub/Sub API endpoints.

If you are running the code locally, you can obtain credentials using this
[Google Cloud SDK](https://cloud.google.com/sdk/docs/) command:

    gcloud auth application-default login

You can also use a
[service account](https://cloud.google.com/iam/docs/understanding-service-accounts)
to authenticate to the Cloud Pub/Sub API endpoints.
If you do so, you must grant the "Pub/Sub Editor" role to the service account.
Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the absolute
path of your service account credential JSON file, e.g.:

    export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/service-account.json

## Tests

To run the tests, first set up a Python Virtual Environment:

    virtualenv -p python2.7 env
    source env/bin/activate
    
Next, install the dependencies:

    pip install -r requirements.txt

Optionally, run lint checks:

    pip install -r requirements-dev.txt
    flake8 pubsub_client/ tests/

If you want to test compatibility with the Google Cloud Client Libraries for
Python, run the script to generate these tests (this step is optional):

    ./generate-compatibility-tests.sh

Finally, run the tests:

    python -m unittest discover
    
## References:

[Google Cloud Client Libraries for Python - Cloud Pub/Sub API](https://google-cloud-python.readthedocs.io/en/latest/pubsub/index.html)

[Google Cloud Client Libraries for Python - Cloud Pub/Sub Client Types](https://google-cloud-python.readthedocs.io/en/latest/pubsub/types.html)

[Google API Client Library for Python - Cloud Pub/Sub API](https://developers.google.com/api-client-library/python/apis/pubsub/v1)

## Disclaimer

This is not an officially supported Google product.
