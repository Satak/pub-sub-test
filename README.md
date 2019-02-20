# GCP Pub/Sub Test App

This is a test app that utilizes GCP's Pub/Sub event bus to create and modify CMDB records. CMDB in this case is basically a local sqlite database (file called `cmdb.sqlite`) that the flask app creates.

Official documentation:
<https://cloud.google.com/pubsub/>

If you just start the flask dev server by running `python main.py` and not the `subscription.py`, then all the messages will go to the Pub/Sub queue and are not processed or acknowledged.

You can see the unprocessed messages in the `/messages` view. By default every 10 seconds they are resend to the queue so you may need to refresh the page couple times to see them. You can acknowledge the messages ad-hoc by pressing the `ACK` button.

When you run the Python script `subscription.py` to start the subscriber, then all the messages that can be processed are acknowledged and those messages with actions that are not supported (`get` and `update`) are left on the queue as unacknowledged. You need to stop the async subscriber `subscription.py` to able to see the messages again in the messages view.

![Pub Sub image](/img/send-msg-ui.png)
![Pub Sub image](/img/ui.png)

## Prerequisites

- Basic understanding of Google Cloud, it's components, Pub/Sub, and IAM
- Basic understanding of Python, webservices, Flask, database, etc.
- Existing GCP project
  - Pub/Sub enabled
  - Pub/Sub topic created
  - Pub/Sub subscription (pull) created
  - GCP service account created and json key downloaded with these roles:
    - `Pub/Sub Publisher`
    - `Pub/Sub Subscriber`
    - `Pub/Sub Viewer`
- Python 3.6=< (scripts utilizes Python 3.6 f-strings)
  - `flask` library
  - `request` library
  - `google-cloud-pubsub` library

## Environment variables

You need to setup some environment variables first:

- `GOOGLE_APPLICATION_CREDENTIALS` - path to your GCP service account json file
- `SECRET` - flask `secret_key` (use any string or more securely `os.urandom(24)`)
- `GCP_PROJECT` - GCP project ID
- `SUBSCRIPTION_NAME` - GCP Pub/Sub subscription name that you have created
- `TOPIC_NAME` - GCP Pub/Sub topic name that you have created
- `SERVER_ADDRESS` - Web server address where the `/cmdb` route exists. Default is the local flask dev server `http://localhost:5000`

## Components

- `main.py` to run the Flask dev server.
- `subscriber.py` to run the Pub/Sub async subscriber that pulls the messages from Pub/Sub and sends them to `/cmdb` route. If this script is not running, then the messages from the flask web server just goes to the Pub/Sub message bus and they are not processed. Can be seen in the `/messages` view.

## Web Server HTTP Routes

| Method   | Route       | Info |
| -------- |-------------| -----|
| GET      | `/`         | Redirect to `/message` |
| GET      | `/message`  | View to send messages to the Pub/Sub queue |
| POST     | `/message`  | Send message to the Pub/Sub message queue |
| GET      | `/messages` | View to see the unprocessed messages in the Pub/Sub queue |
| GET      | `/cmdb`  | View to see the records in the CMDB sqlite database |
| POST     | `/cmdb`  | Route to handle the form request. If the action type is `create` it will create a new CMDB record and if the type is `delete` it will delete the record based on `vm_name` and `namespace` attributes |
| POST     | `/ack/<string:ack_id>`  | Acknowledge the message by it's `ack_id` |


## Architecture

![Pub Sub image](/img/pub_sub.png)
