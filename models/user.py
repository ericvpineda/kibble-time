from .shared import db
from datetime import datetime 

class User(db.Model):
    _id = db.Column("_id", db.Integer, primary_key=True)
    phone = db.Column("phone", db.BigInteger, nullable=False)
    pet_id = db.Column("pet_id", db.Integer, db.ForeignKey("pet._id"))
    status = db.Column("status", db.Integer, nullable=False)
    date_created = db.Column("date_created", db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User: {self._id}, phone: {self.phone}, pet: {self.pet_id}, status: {self.status}>'  