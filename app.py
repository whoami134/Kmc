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
from flask import request
from flask_restful import Resource
from bson.objectid import ObjectId

class Register(Resource):
    def post(self):
        data = request.get_json()
        name = data['name']
        email = data['email']
        password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        role = data['role']
        edu_verified = False

        user = {
            "name": name,
            "email": email,
            "password": password,
            "role": role,
            "edu_verified": edu_verified,
            "profile": {
                "bio": "",
                "education": "",
                "experience": "",
                "ratings": [],
                "average_rating": 0
            }
        }
        user_id = db.users.insert_one(user).inserted_id
        return {"message": "User registered successfully", "user_id": str(user_id)}, 201

api.add_resource(Register, '/register')
from flask_jwt_extended import create_access_token

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        user = db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user['password'], password):
            access_token = create_access_token(identity=str(user['_id']))
            return {"access_token": access_token}, 200
        return {"message": "Invalid credentials"}, 401

api.add_resource(Login, '/login')
from flask_jwt_extended import jwt_required, get_jwt_identity

class Profile(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if user:
            return user, 200
        return {"message": "User not found"}, 404

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        update_fields = {}
        if 'bio' in data:
            update_fields['profile.bio'] = data['bio']
        if 'education' in data:
            update_fields['profile.education'] = data['education']
        if 'experience' in data:
            update_fields['profile.experience'] = data['experience']
        
        db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
        return {"message": "Profile updated successfully"}, 200

api.add_resource(Profile, '/profile')
