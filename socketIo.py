from flask import current_app, g
from flask_socketio import SocketIO


def get_socketio():
    if 'socketio' not in g:
        g.socketio = SocketIO(current_app)
    return g.socketio