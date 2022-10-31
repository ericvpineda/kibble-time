from flask import Flask, render_template, request, redirect
from models.shared import db
from models.pet import Pet
from models.user import User
from phonenumbers import parse, is_valid_number
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        phone_raw = request.form['phone']
        phone_obj = parse(phone_raw, None)
        phone_clean = phone_obj.national_number
        
        if is_valid_number(phone_obj):
            onboard(phone_clean)
            return redirect('/')

        else:
            # Note: Use flash
            print("ERROR: Invalid number")

    return render_template('index.html')


def onboard(phone_number):

    user_exists = User.query.filter_by(phone=phone_number).first()

    if user_exists:
        message = "Notice: user with that phone number already exists. For more options, please reply 'HELP'."
        send_to_user(phone_number, message)
    else: 
        create_new_user(phone_number, db)
        message = "Welcome to Kibble Time! If you want to proceed to make an account, please reply 'YES'. If not, reply 'STOP'."
        send_to_user(phone_number, message)

def create_new_user(phone_number, db):
    new_user = User(phone=phone_number, status=0)
    db.session.add(new_user)
    db.session.commit()

def send_to_user(phone_number, message):

    print("Sending message to user...")
    print(message)

    # account_sid = environ['TWILIO_ACCOUNT_SID']
    # auth_token = environ['TWILIO_AUTH_TOKEN']

    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #         body=message,
    #         from_='+13609269872',
    #         to=phone_number

# Note:
# - Status values: 
#     - 0 = setting name 
#     - 1 = seting pet name 
#     - 2 = set fed_lunch = true 
#     - 3 = set fed_lunch = false
#     - 4 = set fed_dinner = true  
#     - 5 = set fed_dinner = false
@app.route("/sms", methods=["GET", "POST"])
def receive_from_user():

    body = request.values.get("Body", None)
    resp = MessagingResponse()

    # Get user info 
    client_phone_number = request.values.get("From")
    client = User.query.filter_by(phone=client_phone_number).first()
    pet = None 
    
    if client.pet_id != None: 
        pet = Pet.query.filter_by(_id=client.pet_id).first()

    # Note: Need to sanitize message
    if body == "YES":
        content = "Great, you are confirmed! Please enter the name that we can call you by."
        resp.message(content)
    elif client.status == 0:

        if len(body) > 20: 
            content = "Sorry, please limit name length to 20 characters."
        else: 
            client.status = 1
            client.name = body
            db.session.commit()
            content = f"Nice to meet you ${body}. Please enter your pet's name you want to track their meal habits."
    elif client.status == 1:
        if len(body) > 20: 
            content = "Sorry, please limit name length to 20 characters."
        else:
            new_pet = create_new_pet(body)
            client.pet_id = new_pet._id
            client.status = 2
            db.session.commit()
    elif client.status == 2:

        feed_map = {False : "HAS", True : "HAS NOT"}

        if body == f"check":
            content = f"${pet.name} ${feed_map[pet.fed_lunch]} been feed Lunch. And ${pet.name} ${feed_map[pet.fed_lunch]} been fed Dinner."
        elif body == "lunch done":
            content = f"${pet.name} had a yummy lunch and is happy to have you as an owner :)"
            pet.fed_lunch = True 
            db.session.commit()
        elif body == "lunch reset":
            content = f"Lunch for ${pet.name} has been reset. ${pet.name} will need to be fed lunch."
            pet.fed_lunch = False 
            db.session.commit()
        elif body == "dinner reset":
            content = f"Dinner for ${pet.name} has been reset. ${pet.name} will need to be fed dinner."
            pet.fed_dinner = False 
            db.session.commit()
        elif body == "dinner done":
            content = f"${pet.name} was feed a healthy dinner and is ready for bed time!"
            pet.fed_dinner = True 
            db.session.commit()
        else:
            content = "Sorry, there is no command with that message. Please try again."

    else: 
        content = "Thank you for using Kibble Time. Good bye!"
 
    resp.message(content)
    return str(resp)

def create_new_pet(name):
    new_pet = Pet(name=name)
    db.session.add(new_pet)
    db.session.commit()
    return new_pet

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)