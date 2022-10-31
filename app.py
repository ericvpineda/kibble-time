from flask import Flask, render_template, request, redirect
from models.shared import db
from models.pet import Pet
from models.user import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def index():


    # print(new_pet)
    # for user in User.query.all():
    #     print(user)
    # if request.method == "POST":
    #     phone_number = request.form['phone']
    # return redirect('/')
    # else:
    return render_template('index.html')





if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=True)