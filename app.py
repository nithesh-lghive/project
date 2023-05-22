from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
import jwt
from apis import documents,api
from flask_migrate import Migrate
from flask_restx import Resource,Namespace
from functools import wraps
from flask import request
from datetime import datetime,timedelta
from random import randint


app = Flask(__name__)
mail = Mail(app)


app.config['SECRET_KEY'] == 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'userapi001@gmail.com'
app.config['MAIL_PASSWORD'] = 'dmudtmvmibburywd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



app.register_blueprint(documents)

db = SQLAlchemy(app)
migrate = Migrate(app,db)


with app.app_context():
     db.init_app
     db.create_all()
     db.session.commit()

otplist = []

@app.route('/',methods = ['GET'])
def index():
    return 'Api loading...... Please set doc to the url.....'
##################   models   #############################

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    public_id = db.Column(db.String(50), unique = True)
    username = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),nullable = False)
    password = db.Column(db.String(5),nullable = False)
    role = db.Column(db.String(100),default = 'Not defined')

    def __init__(self,public_id,username,email,password):
        self.username = username
        self.email = email
        self.password = password
        self.public_id= public_id
  
    
    def json(self):
        return {'public-id':self.public_id,
                'Username':self.username,
                'Email':self.email,
                'Role':self.role}
    


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

aru.add_argument('id',type = int,help = 'Enter user ID!')
kl.add_argument('username',type = str,help = 'Enter the name of the user')
kl.add_argument('email',type = str,help = 'Enter the Email')
kl.add_argument('password',type = str,help = 'Enter the password')

upt.add_argument('ID',type=int,help= 'Enetr ID')
upt.add_argument('Name',type=str,help= 'Name')
upt.add_argument('Email',type=str,help= 'Email')
upt.add_argument('Password',type=str, help= 'Password')


################## User model  ##############################  

@user.route('/')
@user.doc(responses = {200:"ok",400:'not found'})
class Users(Resource):
    global data
    @user.doc(security='apikey')
    @user.expect(aru)
    @token_required
    def get(self):
        args  = aru.parse_args()
        id = args.get('id')
      
        try:
            users = User.query.filter_by(id=id).first()
            return users.json()
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
            user = User.query\
                .filter_by(email = email)\
                .first()
            if not user:
                users = User(username = username,email= email, password= password)
                db.session.add(users)
                db.session.commit()
                return users.json()
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
            user= User.query.filter_by(id =id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return f" ID {id} is successfully deleted"
            else:
                return f" ID {id} is not found"
        except Exception as e:
            return {'Delete unsuccessfull'}
        

    @user.doc(security='apikey')
    @user.expect(upt)
    @token_required
    def put(self):
        args = upt.parse_args()
        id = args.get('ID')
        uname = str.capitalize(args.get("Name"))
        uemail = str.lower(args.get('Email'))
        upassword = args.get('Password')
        
       

        try:
            users= User.query.filter_by(id =id).first()
            if users:
                users.username = uname
                users.email = uemail
                users.password = upassword
                db.session.commit()
                return users.json()
        except Exception as e:
            return f"{id} not found"
        
        

@user.route('/all')
@user.doc(responses = {200:"ok",400:'not found'})
class Alluser(Resource):
    @token_required
    @user.doc(security='apikey')
    def get(self):
        users =  User.query.all()
        return [user.json() for user in users]
    

        
####################################################### 



#################  JWT Security ##########################

auth_user = Namespace('Login','login page')

log = auth_user.parser()
fgt = auth_user.parser()
o = auth_user.parser()


log.add_argument('username',type = str, help = 'Enter Username')
log.add_argument('password',type = str,help = 'Enter Password')
fgt.add_argument('email',type = str,help = 'Enter email to recieve otp')
o.add_argument('otp',type = str,help = 'Enter otp')
o.add_argument('email',type = str,help = 'Enter Email')
o.add_argument('new_pass',type = str,help = 'Enter new password')

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
  
        user = User.query.filter_by(username = username).first()
    
        if not user:
            return 'User not found',401
        
        if user:
            if password == user.password:
           
                token = jwt.encode({'username' : user.username, 
                                    'exp' : datetime.utcnow() + timedelta(minutes=45)},
                                    'secret' ,algorithm="HS256")
                return {'token' : token}
            else:
                return 'Wrong password ',403

################################################################################

@auth_user.route('/forgot_password')
@auth_user.doc(responses = {200:"ok",400:'not found'})
class Forgot(Resource):
    
    @auth_user.expect(fgt)
    def post(self):
        args = fgt.parse_args()
        email = args.get('email')
        user = User.query.filter_by(email = email).first()
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
########################################################################################       
        
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
                users= User.query.filter_by(email =email).first()
                if users:
                    users.password = new_pass
                    db.session.commit()
                    return  {'Password successfully changed ...new pass word is':new_pass}
            else:
                return "Invalid OTP"

################# User role management  #######################################

userrole = Namespace('User Role Management','User role')
rl = userrole.parser()

rl.add_argument('id',type = int, help = 'Enter Id to update Role')
rl.add_argument('role',type = str,help = 'What is role of user')


@userrole.route('/')
@userrole.doc(responses = {200:"ok",400:'not found',500:'internal server error'})
class Update(Resource):
    @userrole.doc(security='apikey')
    @token_required
    @userrole.expect(rl)
    def put(self):
        args = rl.parse_args()
        id = args.get('id')
        role = str.capitalize(args.get('role'))
       

        try:
            user= User.query.filter_by(id =id).first()
            if user:
                user.role = role
                db.session.commit()
                return user.json()
            else:
                return f"{id} not found"
        except Exception as e:
            return {'Cannot update'}
        
#########################################################


########### Adding Namespaces ######################  

api.add_namespace(user)
api.add_namespace(userrole)
api.add_namespace(auth_user)
 ####################################################

if __name__ == '__main__':
    app.run(debug=True)