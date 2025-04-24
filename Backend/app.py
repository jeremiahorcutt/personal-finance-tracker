import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_cors import CORS
from dotenv import load_dotenv


app = Flask(__name__, template_folder="templates", static_folder="statics")
CORS(app)
load_dotenv()
# configurations
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
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

    user = db.relationship("User", backref=db.backref("transactions", lazy=True))

class Categroy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False)


# routes
@app.route('/')
def home():
  return render_template('index.html')  

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
      data = request.get_json()

      if not data or not all(k in data for k in ["email", "password"]):
          return jsonify({"error": "Missing email or password"}), 400

      user = User.query.filter_by(email=data['email']).first()

      if not user or not check_password_hash(user.password, data['password']):
          return jsonify({"error": "Invalid credentials"}), 401

      access_token = create_access_token(identity=user.id)
      return jsonify({"access_token": access_token, "user_id": user.id}), 200
    return render_template('login.html')

#POST new user
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
     
      data = request.get_json()
        #hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
      new_user = User(
          username=data["username"], 
          email=data["email"], 
          password=data["password"]
     )
      db.session.add(new_user)
      db.session.commit()
      return jsonify({"message": "User registered!"})
    return render_template('register.html')

#POST transactions
@app.route("/transactions", methods=["POST"])
@jwt_required()
def add_transaction():
    data = request.get_json()
    if not data or not all(k in data for k in ["user_id", "type", "amount", "category"]):
        return jsonify({"error": "Missing required fields"}), 400

    if data["type"] not in ["income", "expense"]:
        return jsonify({"error": "Invalid transaction type"}), 400
    
    new_transaction = Transaction(
        user_id=get_jwt_identity(),
        amount=data["amount"],
        category=data["category"],
        description=data["description"],
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({"message": "Transaction added!"})

#GET all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    transactions_list = [
        {
            "id": t.id,
            "user_id": t.user_id,
            "type": t.type,
            "amount": t.amount,
            "category": t.category,
            "description": t.description,
            "date": t.date.strftime("%Y-%m-%d %H:%M:%S")
        }
        for t in transactions
    ]

    return jsonify(transactions_list), 200

#GET transactions by id
@app.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    return jsonify({
        "id": transaction.id,
        "user_id": transaction.user_id,
        "type": transaction.type,
        "amount": transaction.amount,
        "category": transaction.category,
        "description": transaction.description,
        "date": transaction.date.strftime("%Y-%m-%d %H:%M:%S")
    }), 200


if __name__ == "__main__":
    app.run(debug=True)