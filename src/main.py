import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort
)
from conf import (
    CUSTOMERS,
    SECRET
)
from functions import (
    get_messages_sync,
    insert_cmdb_record,
    ack_message,
    send_message,
    get_vms,
    delete_record,
    execute_sql_cmd
)
from sql_queries import CREATE_TABLE

app = Flask(__name__)
app.secret_key = SECRET


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
        res = delete_record(
            vm_name=data['vm_name'], namespace=data['namespace'])
        return jsonify(res), res['status_code']
    else:
        return jsonify({'error': 'action not supported yet'}), 400


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
    now = datetime.datetime.now()
    full_message = f'{now.hour}:{now.minute}:{now.second} - {request.form["message"]}'
    res = send_message(
        data=full_message,
        action=request.form['action'],
        vm_name=request.form['vm_name'],
        namespace=request.form['namespace']
    )
    flash(res)
    return redirect(url_for('message'))


if __name__ == '__main__':
    execute_sql_cmd(CREATE_TABLE)
    app.run(debug=True, threaded=True)
