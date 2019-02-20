import time
from google.cloud import pubsub_v1
import requests

from conf import (
    PROJECT_ID,
    SUBSCRIPTION_NAME,
    TOPIC_NAME,
    SERVER_ADDRESS
)

CMDB_URL_ENDPOINT = f'{SERVER_ADDRESS}/cmdb'
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)


def callback(message):
    json_data = {
        'namespace': message.attributes['namespace'],
        'action': message.attributes['action'],
        'message': message.data.decode(),
        'vm_name': message.attributes['vm_name']
    }
    res = requests.post(CMDB_URL_ENDPOINT, json=json_data)
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
