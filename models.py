from database import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), nullable=False, index=True)
    type = db.Column(db.String(10), nullable=False)  # "expense" | "income"
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(60), nullable=False, default="Geral")
    description = db.Column(db.String(255), nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M"),
        }


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), nullable=False, unique=True, index=True)
    name = db.Column(db.String(100), default="")
    monthly_goal = db.Column(db.Float, default=0.0)
    goal_alerted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "phone": self.phone,
            "name": self.name,
            "monthly_goal": self.monthly_goal,
        }
