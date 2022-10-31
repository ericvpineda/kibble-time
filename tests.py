from distutils.log import debug
import unittest
from flask import Flask
from models.shared import db
from models.user import User
from models.pet import Pet
from app import *

def setup_db():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
    db.init_app(app)
    app.app_context().push()

class OnBoardTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        setup_db()
        db.create_all()

    @classmethod
    def tearDownClass(self):
        db.drop_all()

    def create_new_user_test(self):
        phone_number = "9255491000"
        create_new_user(phone_number, db)
        new_user = User.query.filter_by(phone=phone_number).first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.status, 0)
        self.assertEqual(new_user.pet_id, None)
        self.assertEqual(new_user.name, None)

if __name__ == '__main__':
    unittest.main()