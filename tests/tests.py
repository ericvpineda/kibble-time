import unittest
import mock
from distutils.log import debug
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
    phone_number = "9255491000"
    pet_name = "Miley"
    
    @classmethod
    def setUpClass(self):
        setup_db()
        db.create_all()
        
    @classmethod
    def tearDownClass(self):
        db.drop_all()

    def create_user_test(self):
        create_new_user(self.phone_number, db)
        new_user = User.query.filter_by(phone=self.phone_number).first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.status, 0)
        self.assertEqual(new_user.pet_id, None)
        self.assertEqual(new_user.name, None)

    def create_pet_test(self):
        create_new_pet(self.pet_name)
        new_pet = Pet.query.filter_by(name=self.pet_name).first()
        self.assertIsNotNone(new_pet)
        self.assertEqual(new_pet.name, self.pet_name)
        self.assertFalse(new_pet.fed_lunch)
        self.assertFalse(new_pet.fed_dinner)

    @mock.patch('8_kibble_time.app.send_to_user', "Notice: user with that phone number already exists. For more options, please reply 'HELP'.")
    def onboard_user_exists_test(self):
        create_new_user(self.phone_number, db)
        # onboard(self.phone_number)

if __name__ == '__main__':
    unittest.main()