from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# configurations
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
app.config["SECRET_KEY"] = "your_secret_key"
app.config["JWT_SECRET_KEY"] = "your_jwt_secret"

db = SQLAlchemy(app)
jwt = JWTManager(app)

# database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

# routes
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    new_user = User(username=data["username"], email=data["email"], password=data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered!"})

@app.route("/transactions", methods=["POST"])
@jwt_required()
def add_transaction():
    data = request.get_json()
    new_tx = Transaction(
        user_id=get_jwt_identity(),
        amount=data["amount"],
        category=data["category"],
        description=data["description"],
    )
    db.session.add(new_tx)
    db.session.commit()
    return jsonify({"message": "Transaction added!"})

if __name__ == "__main__":
    app.run(debug=True)