
from flask_restx import Resource,Namespace
from apis.util import token_required
import apis
from app import User,db


data =[{'id':'0','name':'prakash','email':'prak@gmail.com','password':'12345'},
       {'id':'1','name':'nithesh','email':'nith@gmail.com','password':'56789'},
       {'id':'2','name':'divya','email':'div@gmail.com','password':'768999'}]
print(apis.api)







user = Namespace('User Management','User details')

kl = user.parser()
aru = user.parser()


aru.add_argument('id',type = int,help = 'Enter user ID!')
kl.add_argument('id',type = int,help = 'Enter the user id')
kl.add_argument('name',type = str,help = 'Enter the name of the user')
kl.add_argument('email',type = str,help = 'Enter the Email')
kl.add_argument('password',type = int,help = 'Enter the password')


@user.route('/')
@user.doc(responses = {200:"ok",400:'not found'})

class Users(Resource):
    global data
    @user.doc(security='apikey')
    @token_required
    @user.expect(aru)
    def get(self):
        args  = aru.parse_args()
        id = args.get('id')
      
        try:
            value =data[id]
            return value,200
        except Exception as e:
            return {'message':'User Not Found'},400
        
    @user.expect(kl)
    @user.doc(security='apikey')
    @token_required
    def post(self):
        args = kl.parse_args()
        # id = args.get('id')
        name = str.capitalize(args.get('name'))
        email = args.get('email')
        password = args.get('password')
       

        try:
            user = {'id':id,'name':name,'email':email,'password':password}
            data.append(user)
            
            return data[id]
        except Exception as e:
            return {'messag':'unsuccessful'}
        
    @user.expect(aru)
    @user.doc(security='apikey')
    @token_required
    def delete(self):
        args = aru.parse_args()
        id = args.get('id')
        try:
            data.pop(id)
            return data
    
        except Exception as e:
            return {'Delete unsuccessfull'}
        
   
@user.route('/all')
@user.doc(responses = {200:"ok",400:'not found'})
class Alluser(Resource):
    global data
    @user.doc(security='apikey')
    @token_required
    def get(self):
        return data
    
###############################################################
    
userrole = Namespace('User Role Management','User role')
rl = userrole.parser()

rl.add_argument('id',type = int, help = 'Enter Id to update Role')
rl.add_argument('role',type = str,help = 'What is role of user')


@userrole.route('/')
@userrole.doc(responses = {200:"ok",400:'not found'})

class Update(Resource):
    global data
    @userrole.doc(security='apikey')
    @token_required
    @userrole.expect(rl)
    def put(self):
        args = rl.parse_args()
        id = args.get('id')
        role = args.get('role')
        try:
           update = {'role':role}
           data[id].insert(update)          
        
           return data[id]
            
        except Exception as e:
            return {'Cannot update'}
    

    

    





            


       
       
        
    
        
        
       
       
        
