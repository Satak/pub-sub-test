from google.cloud import pubsub_v1
import sqlite3

from conf import (
    PROJECT_ID,
    SUBSCRIPTION_NAME,
    TOPIC_NAME,
    CMDB_DATABASE
)
from sql_queries import (
    CREATE_TABLE,
    INSERT_RECORD,
    DELETE_RECORD,
    SELECT_VMS
)

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)


def execute_sql_cmd(cmd):
    with sqlite3.connect(CMDB_DATABASE) as con:
        cur = con.cursor()
        cur.execute(cmd)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def delete_record(vm_name, namespace):
    data = {
        'vm_name': vm_name,
        'namespace': namespace
    }
    try:
        with sqlite3.connect(CMDB_DATABASE) as con:
            cur = con.cursor()
            cur.execute(DELETE_RECORD, data)
        res = {
            'ok': True,
            'message': f'{vm_name} deleted',
            'status_code': 200
        }
    except Exception as err:
        res = {
            'ok': False,
            'error': str(err),
            'status_code': 400
        }
    print(res)
    return res


def get_vms():
    with sqlite3.connect(CMDB_DATABASE) as con:
        con.row_factory = dict_factory
        cur = con.cursor()
        cur.execute(SELECT_VMS)
        vms = cur.fetchall()
        return vms


def get_messages_sync():
    response = subscriber.pull(subscription_path, max_messages=10, return_immediately=True)
    return [
        {
            'message': received_message.message.data.decode(),
            'namespace': received_message.message.attributes['namespace'],
            'vm_name': received_message.message.attributes['vm_name'],
            'action': received_message.message.attributes['action'],
            'message_id': received_message.message.attributes['message_id'],
            'ack_id': received_message.ack_id
        } for received_message in response.received_messages]


def insert_cmdb_record(namespace, vm_name, message):
    record = {
        'namespace': namespace,
        'vm_name': vm_name,
        'message': message
    }
    try:
        with sqlite3.connect(CMDB_DATABASE) as con:
            cur = con.cursor()
            cur.execute(INSERT_RECORD, record)
            return {
                'ok': True,
                'message': 'record inserted successfully',
                'status_code': 201
            }
    except Exception as err:
        err_msg = f'Something went wrong while inserting data {err}'
        print(err_msg)
        return {
            'ok': False,
            'error': err_msg,
            'status_code': 400
        }


def send_message(data, action, vm_name, namespace):
    future = publisher.publish(
        topic_path,
        data=data.encode(),
        action=action,
        vm_name=vm_name,
        namespace=namespace
    )
    return f'Data: "{data}" Action: "{action}" Name: "{vm_name}" Namespace: "{namespace}" ID: {future.result()}'


def ack_message(ack_id):
    try:
        subscriber.acknowledge(subscription_path, [ack_id])
        return f'Message {ack_id[0:10]}... Acknowledged'
    except Exception as err:
        return f'ERROR while trying to acknowledge: {err}'
