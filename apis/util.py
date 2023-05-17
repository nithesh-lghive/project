from flask import request
from functools import wraps







def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers.get('X-API-KEY')

        if not token:
            return {'message' : 'Token is missing'}, 401

        if token != 'myToken':
            return {'message': 'your token is wrong'}, 401

        return f(*args, **kwargs)
    return decorated