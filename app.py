from flask import Flask
from apis import api


app = Flask(__name__)

app.config['SECRET_KEY'] == 'mysecret'


api.init_app(app)






if __name__ == '__main__':
    app.run(debug=True)