from flask_restx import Api
from .User import user,userrole


api = Api(version='2.0',
          title='user api',
          description='this the user page',)



api.add_namespace(user)
api.add_namespace(userrole)