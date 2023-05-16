# from app import User,db
from flask_restx import Api
from .Users import user,userrole
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
          title='user api',
          description='this the user page',
            authorizations=authorizations, 
            security='apikey')




api.add_namespace(user)
api.add_namespace(userrole)