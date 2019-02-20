import datetime
from google.cloud import pubsub_v1
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
import sqlite3
from os import getenv

app = Flask(__name__)
app.secret_key = getenv('SECRET', 'my-super-secret-secretkey')
project_id = getenv('GCP_PROJECT')
subscription_name = getenv('SUBSCRIPTION_NAME')
topic_name = getenv('TOPIC_NAME')

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

CMDB_DATABASE = 'cmdb.sqlite'
CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS vms (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        vm_name TEXT NOT NULL,
        namespace TEXT NOT NULL,
        message TEXT,
        UNIQUE (vm_name, namespace)
    );
"""
INSERT_RECORD = """
    INSERT INTO vms (namespace, vm_name, message)
    VALUES (:namespace, :vm_name, :message)
"""
DELETE_RECORD = """
    DELETE FROM vms WHERE
    vm_name = :vm_name AND
    namespace = :namespace
"""

# NOTE: you can modify this list
CUSTOMERS = [
    'Customer 1',
    'Customer 2',
    'Customer 3',
]


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
        cur.execute("SELECT id, vm_name, namespace, message FROM vms")
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


@app.route('/')
def root():
    return redirect(url_for('message'))


@app.route('/messages')
def messages():
    return render_template('messages.html', messages=get_messages_sync())


@app.route('/cmdb')
def cmdb_view():
    vms = get_vms()
    return render_template('cmdb.html', vms=vms)


@app.route('/cmdb', methods=['POST'])
def cmdb():
    data = request.get_json(silent=True)
    if data['action'] == 'create':
        res = insert_cmdb_record(
            namespace=data['namespace'],
            vm_name=data['vm_name'],
            message=data['message']
        )
        return jsonify(res), res['status_code']
    elif data['action'] == 'delete':
        res = delete_record(vm_name=data['vm_name'], namespace=data['namespace'])
        return jsonify(res), res['status_code']
    else:
        return jsonify({'error': 'action not supported yet'}), 400


def ack_message(ack_id):
    try:
        subscriber.acknowledge(subscription_path, [ack_id])
        return f'Message {ack_id[0:10]}... Acknowledged'
    except Exception as err:
        return f'ERROR while trying to acknowledge: {err}'


@app.route('/ack/<string:ack_id>', methods=['POST'])
def ack_message_route(ack_id):
    res = ack_message(ack_id)
    flash(res)
    return redirect(url_for('message'))


@app.route('/message')
def message():
    return render_template('message.html', customers=CUSTOMERS)


@app.route('/message', methods=['POST'])
def post_message():
    message = request.form['message']
    action = request.form['action']
    vm_name = request.form['vm_name']
    namespace = request.form['namespace']
    n = datetime.datetime.now()
    full_message = f'{n.hour}:{n.minute}:{n.second} - {message}'
    res = send_message(data=full_message, action=action, vm_name=vm_name, namespace=namespace)
    flash(res)
    return redirect(url_for('message'))


if __name__ == '__main__':
    execute_sql_cmd(CREATE_TABLE)
    app.run(debug=True, threaded=True)
