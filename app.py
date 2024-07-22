from flask import Flask
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/karmacounsel'

api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

from pymongo import MongoClient
client = MongoClient(app.config['MONGO_URI'])
db = client.get_database()

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)
