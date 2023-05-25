from flask import Flask,request,json,jsonify,Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_mail import Mail,Message
import jwt
import uuid
from apis import documents,api
from flask_migrate import Migrate
from flask_restx import Resource,Namespace
from functools import wraps
from flask import request
from datetime import datetime,timedelta
from random import randint
from flask_pymongo import PyMongo
from bson import json_util
from bson.json_util import dumps

app = Flask(__name__)
mail = Mail(app)


app.config['SECRET_KEY'] == 'mysecret'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["MONGO_URI"] = "mongodb://localhost:27017/swagger"
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'userapi001@gmail.com'
app.config['MAIL_PASSWORD'] = 'dmudtmvmibburywd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



app.register_blueprint(documents)

# db = SQLAlchemy(app)
# migrate = Migrate(app,db)
db = PyMongo(app).db

# with app.app_context():
#      db.init_app
#      db.create_all()
#      db.session.commit()

otplist = []

@app.route('/',methods = ['GET'])
def index():
    return 'Api loading...... Please set doc to the url.....'
##################   models   #############################

# class User(db.Model):
#     id = db.Column(db.Integer,primary_key = True)
#     public_id = db.Column(db.String(50), unique = True)
#     username = db.Column(db.String(100),nullable = False)
#     email = db.Column(db.String(100),nullable = False)
#     password = db.Column(db.String(5),nullable = False)
#     role = db.Column(db.String(100),default = 'Not defined')
#     date = db.Column(db.DateTime, default=datetime.utcnow)

#     def __init__(self,public_id,username,email,password,date):
#         self.username = username
#         self.email = email
#         self.password = password
#         self.public_id= public_id
#         self.date = date
  
    
    # def json(self):
    #     return {
    #             'Username':self.username,
    #             'Email':self.email,
    #             'Password':self.password,
    #             'Role':self.role,
    #             'Date Created':str(self.date)
    #             }
    
    # def jsons(self):
    #      return {
    #             'Username':self.username,
    #             'Email':self.email,
    #             'Role':self.role,
    #             'Date Created':str(self.date)}
    
    


###############################################################################


################ token required function  ###########################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-API-KEY' in request.headers:
           token = request.headers.get('X-API-KEY')
        if not token:
            return ({'message' : 'Authorization required !!'}), 401
        try:
            data = jwt.decode(token,'secret', algorithms=["HS256"])
            print(data)
        except:
            return {'message' : 'Token is Invalid  !!'}, 401
        return  f(*args, **kwargs)
  
    return decorated


###########################################################

############## namespaces #################################

user = Namespace('User Management','User details')

kl = user.parser()
aru = user.parser()
upt = user.parser()
all = user.parser()

aru.add_argument('id',required = True,type = str,help = 'Enter user ID!')
kl.add_argument('username',type = str,required = True,help = 'Enter the name of the user')
kl.add_argument('email',type = str,required = True,help = 'Enter the Email')
kl.add_argument('password',type = str,required = True,help = 'Enter the password')
all.add_argument('filter',type = str,choices=("email", "role","first modified","last modified","first modified with limit","last modified with limit"),help = 'sort by')
all.add_argument('email',type = str,help = 'Enter the email')
all.add_argument('role',type = str,help = 'Enter the role')
all.add_argument('limit',type = int,help = 'Enter limit(optional)')
all.add_argument('offset',type = int,help = 'Enter offset(optional)')

upt.add_argument('ID', required = True, type=str,help= 'Enter ID')
upt.add_argument('Name',type=str,help= 'Name')
upt.add_argument('Email',type=str,help= 'Email')



################## User model  ##############################  

@user.route('/')
@user.doc(responses = {200:"ok",400:'not found'})
class Users(Resource):
    def json(self):
        return{'username':self.username
        }


    @user.doc(security='apikey')
    @user.expect(aru)
    @token_required
    def get(self):
        args  = aru.parse_args()
        pub_id = args.get('id')      
        try:
           
            return Response(
                     json_util.dumps(db.User.find_one({'public_id':pub_id})),
                        mimetype='application/json'
)            
        except Exception as e:
            return {'message':'User Not Found'},400
        
    @user.expect(kl)
    @user.doc(security='apikey')
    @user.response(200,'Successfully added')
    def post(self):
        args = kl.parse_args()
        username = str.capitalize(args.get('username'))
        email = str.lower(args.get('email'))
        password = args.get('password')
       

        try:
            user = db.User.find_one({'email':email})
            if not user:
                db.User.insert_one({'public_id': str(uuid.uuid4()),
                             'username' :username,
                             'email': email,
                               'password': password,
                               'date' :datetime.utcnow()})
       

                json ={'Username':username,
                'Email':email,
                'Password':password,
                'Date Created':str(datetime.utcnow())}
                return json
            else:
                return 'User already exists. Please Log in.', 202
        except Exception as e:
            return {'messag ':'unsuccessful'}
        
    
    @user.expect(aru)
    @user.doc(security='apikey')
    @user.response(200,'Successfully deleted')
    @token_required
    def delete(self):
        args = aru.parse_args()
        id = args.get('id')
        try:
            user= db.User.find_one({'public_id':id})
            if user:
                db.User.delete_one({'public_id':id})
                return f"ID  is successfully deleted"
           
            return "Not found"
        except Exception as e:
            return {'Delete unsuccessfull'}
        

    @user.doc(security='apikey')
    @user.expect(upt)
    @token_required
    def put(self):
        args = upt.parse_args()
        user_id = args.get('ID')
        uname = args.get("Name")
        uemail = args.get('Email')
        
        try:
            users= db.User.find_one({'public_id' :user_id})
            if users:
                
                if uname:
                    db.User.update_one({'public_id' :user_id},
                                   {'$set':{'username':uname}})
                    
                mails = db.User.find_one({'email' :uemail})
                if uemail and not mails:
                    db.User.update_one({'public_id' :user_id},
                                   {'$set':{'email':uemail}})
                
                db.User.update_one({'public_id' :user_id},
                                   {'$set':{'date':datetime.utcnow()}})
                
                return Response(
                     json_util.dumps(db.User.find_one({'public_id':user_id})),
                        mimetype='application/json')
                s
                
                
        except Exception as e:
            return f"{user_id} not found"
        
        

@user.route('/all')
@user.doc(responses = {200:"ok",400:'not found'})
class Alluser(Resource):
    @user.expect(all)
    @token_required
    @user.doc(security='apikey')
    def get(self):
        args = all.parse_args()
        filter = args.get('filter')
        email = args.get('email')
        role = args.get('role')
        lim = args.get('limit')
        offset = args.get('offset')
        

        if  filter == 'email' and email :
            checks = db.User.find_one({'email' : email})
            return Response(json_util.dumps(checks),mimetype='application/json')
        
        if  filter == 'role' and role :
            checks = db.User.find_one({'role':role})
            return Response(json_util.dumps(checks),mimetype='application/json')
        
        if  filter == 'first modified':
            checks = db.User.find().sort('date')
            return Response(json_util.dumps(checks),mimetype='application/json')
        
        if  filter == 'last modified':
            checks = db.User.find().sort('date',-1)
            return Response(json_util.dumps(checks),mimetype='application/json')
        
        if  filter == 'first modified with limit' and lim:
            checks = db.User.find().sort('date').limit(lim)
            return Response(json_util.dumps(checks),mimetype='application/json')
        
        if  filter == 'last modified with limit' and lim:
            checks = db.User.find().sort('date',-1).limit(lim)
            return Response(json_util.dumps(checks),mimetype='application/json')
        
        if lim or offset:
            query = db.User.find().limit(lim)
            return Response(json_util.dumps(query),mimetype='application/json')
        
       
        query = db.User.find({})
        return Response(json_util.dumps(query),mimetype='application/json')
    

        
# ####################################################### 



# #################  JWT Security ##########################

auth_user = Namespace('Login','login page')

log = auth_user.parser()
fgt = auth_user.parser()
o = auth_user.parser()


log.add_argument('username',required = True,type = str, help = 'Enter Username')
log.add_argument('password',required = True,type = str,help = 'Enter Password')
fgt.add_argument('email',type = str,required = True,help = 'Enter email to recieve otp')
o.add_argument('otp',type = str,required = True,help = 'Enter otp')
o.add_argument('email',type = str,required = True,help = 'Enter Email')
o.add_argument('new_pass',type = str,required = True,help = 'Enter new password')

@auth_user.route('/')
@auth_user.doc(responses = {200:"ok",400:'not found',500:'internal server error'})

class Login(Resource):
    @auth_user.expect(log)
    def post(self):
        args = log.parse_args()
        username = args.get('username')
        password = args.get('password')
        
        if not password or not username :
           
           return "Email or Password can't be empty"
  
        user = db.User.find_one({'username':username})
        
    
        if not user:
            return 'User not found',401
        
        psw = db.User.find_one({'password':password})
        if user:
            if psw:
           
                token = jwt.encode({'username' :username, 
                                    'exp' : datetime.utcnow() + timedelta(minutes=45)},
                                    'secret' ,algorithm="HS256")
                # key =  db.User.find_one({'username':username})
                return {'token' : token,
                        }
            else:
                return 'Wrong password ',403

# ################################################################################

@auth_user.route('/forgot_password')
@auth_user.doc(responses = {200:"ok",400:'not found'})
class Forgot(Resource):
    
    @auth_user.expect(fgt)
    def post(self):
        args = fgt.parse_args()
        email = args.get('email')
        user = db.User.find_one({'email':email})
        if not user:
          return 'Email not found...  or  Invalid Email'
        if user:
            otp = randint(1111,9999)
            otplist.append(str(otp))
    
            msg = Message(
                    'OTP',
                    sender ='userapi001@gmail.com',
                    recipients = [email]
                   )
            msg.body = str(otp)
            mail.send(msg)
            return 'OTP Sent...'
# ########################################################################################       
        
@auth_user.route('/otp')
@auth_user.doc(responses = {200:"ok",400:'not found',500:'internal server error'})
class Otp(Resource):
    @auth_user.expect(o)
    def post(self):
        args = o.parse_args()
        otp = args.get('otp')
        new_pass = args.get('new_pass')
        email = args.get('email')
        print(otplist)
        for u_otp in otplist:
            if otp == u_otp:
                users= db.User.find_one({'email':email})
                if users:
                    db.User.update_one({'email' :email},
                                   {'$set':{'password':new_pass}})
                    
                    return  {'Password successfully changed ...new pass word is':new_pass}
            else:
                return "Invalid OTP"

# ################# User role management  #######################################

# userrole = Namespace('User Role Management','User role')
# rl = userrole.parser()

# rl.add_argument('id',required = True,type = str, help = 'Enter Id to update Role')
# rl.add_argument('role',required = True,type = str,help = 'What is role of user')


# @userrole.route('/')
# @userrole.doc(responses = {200:"ok",400:'not found',500:'internal server error'})
# class Update(Resource):
#     @userrole.doc(security='apikey')
#     @token_required
#     @userrole.expect(rl)
#     def put(self):
#         args = rl.parse_args()
#         id = args.get('id')
#         role = str.capitalize(args.get('role'))
       

#         try:
#             user= User.query.filter_by(public_id =id).first()
#             if user:
#                 user.role = role
#                 user.date = datetime.utcnow()
#                 db.session.commit()
#                 return user.json()
#             else:
#                 return f"{id} not found"
#         except Exception as e:
#             return {'Cannot update'}
        
#########################################################


########### Adding Namespaces ######################  

api.add_namespace(user)
# api.add_namespace(userrole)
api.add_namespace(auth_user)
 ####################################################

if __name__ == '__main__':
    app.run(debug=True)