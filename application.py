from flask import Flask, render_template, request, redirect, flash
from sqlalchemy import create_engine
from models.shared import db
from models.pet import Pet
from models.user import User
from phonenumbers import parse, is_valid_number
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from os import environ
from dotenv import load_dotenv
import pymysql

load_dotenv()

status = {True : "ALREADY FED", False : "NOT FED"}

development_db = 'sqlite:///test.db'
production_db = "mysql+pymysql://{0}:{1}@{2}:3306/{3}".format(
    environ['AWS_DB_USERNAME'],
    environ['AWS_DB_PW'],
    environ['AWS_DB_HOST'],
    environ['AWS_DB_NAME']
)

application = Flask(__name__)
application.app_context().push()
application.config['SQLALCHEMY_DATABASE_URI'] = production_db
application.secret_key = environ['FLASH_SECRET']
db.init_app(application)
db.create_all()

@application.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        phone_raw = request.form['phone']
        phone_obj, phone_clean = clean_phone_number("+1" + phone_raw)

        if is_valid_number(phone_obj):
            flash("Success! Please check your text messages for next steps.", "success")
            onboard(phone_clean) 

        else:
            flash("Error: Please use a valid US phone number!", "error")
        return redirect('/')

    return render_template('index.html')

def send_to_user(phone_number, message):

    account_sid = environ['TWILIO_ACCOUNT_SID']
    auth_token = environ['TWILIO_AUTH_TOKEN']

    client = Client(account_sid, auth_token)
    message = client.messages.create(
            body=message,
            from_='+13609269872',
            to=phone_number
    )

@application.route("/sms", methods=["GET", "POST"])
def receive_from_user():
    
    data = request.values.get("Body", None)

    if data: 

        name = data.strip()
        body = name.lower()
        resp = MessagingResponse()

        # Get user info 
        client_phone_raw = request.values.get("From")
        _, client_phone_number = clean_phone_number(client_phone_raw)
        client = User.query.filter_by(phone=client_phone_number).first()
        pet = None 
        
        if client and client.pet_id != None: 
            pet = Pet.query.filter_by(_id=client.pet_id).first()

        # Note: Need to sanitize message
        if body == "yes":
            create_new_user(client_phone_number)
            content = "Great, you are confirmed! Please enter your pet's NAME whom you want to track their meal habits."
        # Status 0 : set client pet name
        elif client.status == 0:
            if len(body) > 20: 
                content = "Sorry, please limit name length to 20 characters."
            else:
                new_pet = create_new_pet(name)
                client.pet_id = new_pet._id
                client.status = 1
                db.session.commit()
                msgs = [
                    f"{new_pet.name} will be happy to have a scheduled meal time! Here are a the commands to know:",
                    f"Reply 'Status' to check {new_pet.name}'s lunch and dinner status.",
                    f"Reply 'Lunch done' to update {new_pet.name}'s lunch status to ALREADLY FED. And reply 'Lunch reset' to reset status to NOT FED."
                ]
                for msg in msgs:
                    send_to_user(client_phone_number, msg)
                content = f"Reply 'Dinner done' to update {new_pet.name}'s dinner status to ALREADLY FED. And reply 'Dinner reset' to reset status to NOT FED."
        # Status 1 : status check and updates
        elif client.status == 1:

            if body == "status":
                content = f"{pet.name}'s lunch status: {status[pet.fed_lunch]}, dinner status: {status[pet.fed_dinner]}"
            elif body == "lunch done":
                pet.fed_lunch = True 
                db.session.commit()
                content = f"Lunch status is set to: {status[pet.fed_lunch]}. {pet.name} had a yummy lunch!"
            elif body == "lunch reset":
                pet.fed_lunch = False 
                db.session.commit()
                content = f"Lunch status is set to: {status[pet.fed_lunch]}. {pet.name} will need to be fed lunch."
            elif body == "dinner done":
                pet.fed_dinner = True 
                db.session.commit()
                content = f"Dinner status is set to: {status[pet.fed_dinner]}. {pet.name} was fed a healthy dinner and is ready for bed!"
            elif body == "dinner reset":
                pet.fed_dinner = False 
                db.session.commit()
                content = f"Dinner status is set to: {status[pet.fed_dinner]}. {pet.name} will need to be fed dinner."
            else:
                content = "Sorry, there is no command with that message. Please try again."

        else: 
            content = "Thank you for using Kibble Time. Good bye!"

        resp.message(content)
        return str(resp)

    return "Error: Page not found."

def onboard(phone_number):

    user_exists = User.query.filter_by(phone=phone_number).first()

    if user_exists:
        message = "Notice: user with that phone number already exists. To stop messages, please reply 'STOP'."
        send_to_user(phone_number, message)
    
    else: 
        message = "Welcome to Kibble Time! To proceed to make an account, please reply 'YES'. If not, reply 'STOP'."
        send_to_user(phone_number, message)

def create_new_user(phone_number):
    new_user = User(phone=phone_number, status=0)
    db.session.add(new_user)
    db.session.commit()

def create_new_pet(name):
    new_pet = Pet(name=name)
    db.session.add(new_pet)
    db.session.commit()
    return new_pet

def clean_phone_number(phone_raw):
    if phone_raw:
        phone_obj = parse(phone_raw, None)
        phone_clean = phone_obj.national_number
        return phone_obj, phone_clean   
    return None, None

# -- Utility Functions -- 

def clean_db():
    db.session.commit()
    db.drop_all()
    db.create_all()

def onboard_test(phone_number):
    db.drop_all()
    db.create_all()
    create_new_user(phone_number)

if __name__ == "__main__":
    application.run(debug=True, port=8000)