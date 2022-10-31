from .shared import db
from datetime import datetime 

class Pet(db.Model):
    _id = db.Column("_id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(20), nullable=False)
    fed_lunch = db.Column("fed_lunch", db.Boolean, default=False)
    fed_dinner = db.Column("fed_dinner", db.Boolean, default=False)
    date_created = db.Column("date_created", db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Pet: {self.name}, lunch: {self.fed_lunch}, dinner: {self.fed_dinner}>'