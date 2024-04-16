#!/usr/bin/env python3
from os import path
from threading import Lock

from flask import Flask, Response, request

app = Flask(__name__)

UPLOAD_DIR = '/tmp'
WRITE_LOCK = Lock()


def save_file(name, data):
    with open(f'{UPLOAD_DIR}/{name}.png', 'wb') as ff:
        ff.write(data)


@app.route('/api/v1/<name>', methods=['POST','PUT'])
def upload(name):
    if request.content_type != 'image/png':
        return Response(status=415, response=f'unsupported mimetype {request.content_type}')

    locked = WRITE_LOCK.acquire(timeout=10)
    if not locked:
        return Response(status=503, response='unable to acquire write lock')

    try:
        save_file(name, request.get_data())
    finally:
        WRITE_LOCK.release()

    return Response(status=201, response='created')


@app.route('/api/v1/<name>', methods=['GET'])
def send(name):
    filename = f'{UPLOAD_DIR}/{name}.png'
    if path.exists(filename):
        return Response(status=200, response=open(filename, 'rb'), mimetype='image/png')

    return Response(status=404, response='file not found')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
