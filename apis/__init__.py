
from flask_restx import Api
from flask import Blueprint

documents = Blueprint('api',__name__,url_prefix='/doc')


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY',
        'username':'username'
    }
}



api = Api(documents,
           version='2.0',
          title='User Apis',
          description='This is the user page',
            authorizations=authorizations, 
            security='apikey')

