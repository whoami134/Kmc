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
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

from itsdangerous import URLSafeTimedSerializer

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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

        token = s.dumps(email, salt='email-confirm')
        link = url_for('confirm_email', token=token, _external=True)
        msg = Message('Confirm your email', sender='your-email@example.com', recipients=[email])
        msg.body = f'Your link is {link}'
        mail.send(msg)

        return {"message": "User registered successfully. Check your email to verify your account.", "user_id": str(user_id)}, 201
class ConfirmEmail(Resource):
    def get(self, token):
        try:
            email = s.loads(token, salt='email-confirm', max_age=3600)
            user = db.users.find_one({"email": email})
            if user:
                db.users.update_one({"email": email}, {"$set": {"edu_verified": True}})
                return {"message": "Email verified successfully"}, 200
        except:
            return {"message": "The confirmation link is invalid or has expired."}, 400

api.add_resource(ConfirmEmail, '/confirm/<token>')
class Session(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        counselor_id = data['counselor_id']
        date = data['date']

        session = {
            "counselor_id": ObjectId(counselor_id),
            "student_id": ObjectId(user_id),
            "date": date,
            "status": "pending",
            "notes": ""
        }
        session_id = db.sessions.insert_one(session).inserted_id
        return {"message": "Session created successfully", "session_id": str(session_id)}, 201

api.add_resource(Session, '/session')
class UpdateSession(Resource):
    @jwt_required()
    def put(self, session_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        status = data['status']
        notes = data.get('notes', "")

        session = db.sessions.find_one({"_id": ObjectId(session_id), "counselor_id": ObjectId(user_id)})
        if session:
            db.sessions.update_one({"_id": ObjectId(session_id)}, {"$set": {"status": status, "notes": notes}})
            return {"message": "Session updated successfully"}, 200
        return {"message": "Session not found or not authorized"}, 404

api.add_resource(UpdateSession, '/session/<session_id>')
class Rating(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        counselor_id = data['counselor_id']
        rating = data['rating']
        review = data['review']

        rating_data = {
            "student_id": ObjectId(user_id),
            "rating": rating,
            "review": review
        }
        db.users.update_one({"_id": ObjectId(counselor_id)}, {"$push": {"profile.ratings": rating_data}})
        
        # Update average rating
        user = db.users.find_one({"_id": ObjectId(counselor_id)})
        ratings = user['profile']['ratings']
        avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
        db.users.update_one({"_id": ObjectId(counselor_id)}, {"$set": {"profile.average_rating": avg_rating}})

        return {"message": "Rating submitted successfully"}, 201

api.add_resource(Rating, '/rating')
class Leaderboard(Resource):
    def get(self):
        counselors = db.users.find({"role": "counselor"}).sort("profile.average_rating", -1).limit(10)
        leaderboard = []
        for counselor in counselors:
            leaderboard.append({
                "name": counselor['name'],
                "average_rating": counselor['profile']['average_rating'],
                "ratings_count": len(counselor['profile']['ratings'])
            })
        return leaderboard, 200

api.add_resource(Leaderboard, '/leaderboard')

