import time
from os import getenv
from google.cloud import pubsub_v1
import requests

project_id = getenv('GCP_PROJECT')
subscription_name = getenv('SUBSCRIPTION_NAME')
topic_name = getenv('TOPIC_NAME')

url = 'http://localhost:5000/cmdb'  # change this to your dev server
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)


def callback(message):
    json_data = {
        'namespace': message.attributes['namespace'],
        'action': message.attributes['action'],
        'message': message.data.decode(),
        'vm_name': message.attributes['vm_name']
    }
    res = requests.post(url, json=json_data)
    if res.ok:
        print('Data:', message.data.decode())
        print('Custom attributes:', message.attributes)
        print('Single attribute (action):', message.attributes['action'])
        print('Single attribute (namespace):', message.attributes['namespace'])
        print('\n')
        message.ack()
    else:
        print(f'Web request not ok for {message}:', res.json(), '\n')

subscriber.subscribe(subscription_path, callback=callback)

# The subscriber is non-blocking. We must keep the main thread from
# exiting to allow it to process messages asynchronously in the background.
print(f'Listening for messages on {subscription_path}\n')
while True:
    time.sleep(60)
