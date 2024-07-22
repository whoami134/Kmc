import unittest
from app import app, db
from flask_testing import TestCase

class BaseTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['MONGO_URI'] = 'mongodb://localhost:27017/karmacounsel_test'
        return app

    def setUp(self):
        # Clear the test database
        db.client.drop_database('karmacounsel_test')

    def tearDown(self):
        # Clear the test database
        db.client.drop_database('karmacounsel_test')
  import json
from tests.base import BaseTestCase

class UserTestCase(BaseTestCase):
    def test_user_registration(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=json.dumps({
                    'name': 'John Doe',
                    'email': 'john.doe@university.edu',
                    'password': 'password123',
                    'role': 'counselor'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('User registered successfully', data['message'])

    def test_user_login(self):
        with self.client:
            # Register a new user
            self.client.post(
                '/register',
                data=json.dumps({
                    'name': 'John Doe',
                    'email': 'john.doe@university.edu',
                    'password': 'password123',
                    'role': 'counselor'
                }),
                content_type='application/json'
            )
            # Login the user
            response = self.client.post(
                '/login',
                data=json.dumps({
                    'email': 'john.doe@university.edu',
                    'password': 'password123'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('access_token', data)
import json
from tests.base import BaseTestCase
from app import s, db

class VerificationTestCase(BaseTestCase):
    def test_email_verification(self):
        with self.client:
            # Register a new user
            response = self.client.post(
                '/register',
                data=json.dumps({
                    'name': 'Jane Doe',
                    'email': 'jane.doe@university.edu',
                    'password': 'password123',
                    'role': 'counselor'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            user_id = data['user_id']
            user = db.users.find_one({"_id": ObjectId(user_id)})
            token = s.dumps(user['email'], salt='email-confirm')
            
            # Verify email
            response = self.client.get(f'/confirm/{token}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('Email verified successfully', data['message'])
            user = db.users.find_one({"_id": ObjectId(user_id)})
            self.assertTrue(user['edu_verified'])
import json
from tests.base import BaseTestCase
from app import db, create_access_token
from bson.objectid import ObjectId

class SessionTestCase(BaseTestCase):
    def test_create_session(self):
        with self.client:
            # Register and verify a counselor
            response = self.client.post(
                '/register',
                data=json.dumps({
                    'name': 'John Counselor',
                    'email': 'john.counselor@university.edu',
                    'password': 'password123',
                    'role': 'counselor'
                }),
                content_type='application/json'
            )
            user_id = json.loads(response.data.decode())['user_id']
            token = s.dumps('john.counselor@university.edu', salt='email-confirm')
            self.client.get(f'/confirm/{token}')
            
            # Register a student
            response = self.client.post(
                '/register',
                data=json.dumps({
                    'name': 'Student User',
                    'email': 'student.user@gmail.com',
                    'password': 'password123',
                    'role': 'student'
                }),
                content_type='application/json'
            )
            student_id = json.loads(response.data.decode())['user_id']

            # Login as student
            response = self.client.post(
                '/login',
                data=json.dumps({
                    'email': 'student.user@gmail.com',
                    'password': 'password123'
                }),
                content_type='application/json'
            )
            access_token = json.loads(response.data.decode())['access_token']
            
            # Create session
            response = self.client.post(
                '/session',
                data=json.dumps({
                    'counselor_id': user_id,
                    'date': '2023-07-21T10:00:00'
                }),
                headers={'Authorization': f'Bearer {access_token}'},
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('Session created successfully', data['message'])
#deploy to heroku next for testing - (dont forget leo!)
