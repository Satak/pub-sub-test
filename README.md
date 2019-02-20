# GCP Pub/Sub Test App

This is a test app that utilizes GCP's Pub/Sub event buss to create and modify CMDB records. CMDb is basically a local sqlite database (local file called `cmdb.sqlite`) that the flask app creates.

Official documentation:
<https://cloud.google.com/pubsub/>

## Prerequisites

- Basic understanding of Google Cloud, it's components, Pub/Sub, and IAM
- Basic understanding of Python, webservices, Flask, database, etc.
- Existing GCP project
  - Pub/Sub enabled
  - Pub/Sub topic created
  - Pub/Sub subscription (pull) created
  - GCP service account created with these roles:
    - `Pub/Sub Publisher`
    - `Pub/Sub Subscriber`
    - `Pub/Sub Viewer`
- Python installed
  - `flask` library
  - `request` library
  - `google-cloud-pubsub` library

## Environment variables

You need to setup some environment variables first:

- `SECRET` - flask `secret_key` (use `os.urandom(24)`)
- `GCP_PROJECT` - GCP project ID
- `SUBSCRIPTION_NAME` - GCP Pub/Sub subscription name
- `TOPIC_NAME` - GCP Pub/Sub topic name
- `SERVER_ADDRESS` - Web server address where the `/cmdb` route exists. Default is the local flask dev server `http://localhost:5000`

## Components

- `main.py` to run the Flask dev server
- `subscriber.py` run the Pub/Sub async subscriber that pulls the messages from Pub/Sub and sends them to `/cmdb` route. If this is not running then the messages from the flask web server goes to the Pub/Sub message buss and are not handled.

## Architecture

![Pub Sub image](/img/pub_sub.png)
