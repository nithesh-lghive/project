
data = {"prakash":"{'salary':'10000'}","ravi":"{'salary':'50000'}"}

from flask_restx import Resource,Namespace

user = Namespace('User','User details')
kl = user.parser()
aru = user.parser()

aru.add_argument('name',type = str,help = 'what is the name !')
kl.add_argument('fname',type = str,help = 'what is the name')
kl.add_argument('salary',type = int,help = 'what is the salary')


@user.route('/')
@user.doc(responses = {200:"ok",400:'not found'})
class User(Resource):
    global data
    @user.expect(aru)
    def get(self):
        args  = aru.parse_args()
        name = args.get('name')
      
        try:
            value =data.get(name)
            return {'Salary':value},200
        except Exception as e:
            return {'message':'not found'},400
        
    @user.expect(kl)
    def post(self):
        args = kl.parse_args()
        fname = args.get('fname')
        salary = args.get('salary')
        print(args)
        print(data)

        try:
            data[fname] = salary
            return data
        except Exception as e:
            return {'messag':'unsuccessful'}
        
    @user.expect(aru)
    def delete(self):
        args = aru.parse_args()
        name = args.get('name')
        try:
            data.pop(name)
            return f"{name} successfully deleted ...."
        
        except Exception as e:
            return {'Delete unsuccessfull'}
        

    @user.expect(kl)
    def put(self):
        args = kl.parse_args()
        fname = args.get('fname')
        salary = args.get('salary')
        try:
            data[fname] = salary
            return {fname:salary}
        except Exception as e:
            return {'Cannot update'}
            


       
       
        
    
        
        
       
       
        
