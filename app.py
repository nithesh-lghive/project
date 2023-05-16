from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apis import documents
from flask_migrate import Migrate


app = Flask(__name__)

app.config['SECRET_KEY'] == 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False

db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.register_blueprint(documents)


@app.route('/',methods = ['GET'])
def index():
    return 'Api loading...... Please set doc to the url.....'

with app.app_context():
     db.init_app
     db.create_all()
     db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),nullable = False)
    password = db.Column(db.Integer,nullable = False)
    role = db.Column(db.String(100),default = 'not defined')

    def __init__(self,username,email,password,role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def json(self):
        return {'Id':self.id,
                'Username':self.username,
                'Email':self.email,
                'Role':self.role}
    





if __name__ == '__main__':
    app.run(debug=True)