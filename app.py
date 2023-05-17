from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apis import documents,api
from flask_migrate import Migrate
from flask_restx import Resource,Namespace
from apis.util import token_required
# from flask_jwt import JWT

 
 
app = Flask(__name__)

app.config['SECRET_KEY'] == 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.register_blueprint(documents)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
# jwt = JWT(app,authenticate,identity)

with app.app_context():
     db.init_app
     db.create_all()
     db.session.commit()



@app.route('/',methods = ['GET'])
def index():
    return 'Api loading...... Please set doc to the url.....'
##################   models   #############################

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),nullable = False)
    password = db.Column(db.Integer,nullable = False)
    role = db.Column(db.String(100),default = 'Not defined')

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
  
    
    def json(self):
        return {'Id':self.id,
                'Username':self.username,
                'Email':self.email,
                'Password':self.password,
                'Role':self.role}
    


################################################################################
# username_table = {u.username:u for u in User}
# userid_table = {u.id:u for u in User}

# def authenticate(name,password):
#     user = username_table.get(name,None)
#     if user and password == user.password:
#         return user
    
# def identity(payload):
#     id = payload['identity']
#     return userid_table.get(id,None)


# jwt = JWT(app,authenticate,identity)


############## namespaces #################################

user = Namespace('User Management','User details')

kl = user.parser()
aru = user.parser()
upt = user.parser()

aru.add_argument('id',type = int,help = 'Enter user ID!')
kl.add_argument('username',type = str,help = 'Enter the name of the user')
kl.add_argument('email',type = str,help = 'Enter the Email')
kl.add_argument('password',type = int,help = 'Enter the password')

upt.add_argument('ID',type=int,help= 'Enetr ID')
upt.add_argument('Name',type=str,help= 'Name')
upt.add_argument('Email',type=str,help= 'Email')
upt.add_argument('Password',type=str, help= 'Password')


################################################################

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
            users = User.query.filter_by(id=id).first()
            return users.json()
        except Exception as e:
            return {'message':'User Not Found'},400
        
    @user.expect(kl)
    @user.doc(security='apikey')
    @token_required
    @user.response(200,'Successfully added')
    def post(self):
        args = kl.parse_args()
        username = str.capitalize(args.get('username'))
        email = str.lower(args.get('email'))
        password = args.get('password')
       

        try:
            users = User(username = username,email= email, password= password)
            db.session.add(users)
            db.session.commit()
            return users.json()
        except Exception as e:
            return {'messag ':'unsuccessful'}
        
    
    @user.expect(aru)
    @user.doc(security='apikey')
    @token_required
    @user.response(200,'Successfully deleted')
    def delete(self):
        args = aru.parse_args()
        id = args.get('id')
        try:
            user= User.query.filter_by(id =id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return f" ID {id} is successfully deleted"
        except Exception as e:
            return {'Delete unsuccessfull'}
        

    @user.doc(security='apikey')
    @token_required
    @user.expect(upt)
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
    @user.doc(security='apikey')
    @token_required
    
    def get(self):
        users =  User.query.all()
        return [user.json() for user in users]
    

        
 #######################################################3   

userrole = Namespace('User Role Management','User role')
rl = userrole.parser()

rl.add_argument('id',type = int, help = 'Enter Id to update Role')
rl.add_argument('role',type = str,help = 'What is role of user')


@userrole.route('/')
@userrole.doc(responses = {200:"ok",400:'not found'})

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
# api.add_namespace(auth_user)

####################################################


#################  JWT Security ##########################




####################################################



if __name__ == '__main__':
    app.run(debug=True)